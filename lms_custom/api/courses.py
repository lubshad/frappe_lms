import frappe

from lms_custom.api._utils import expand_relative_urls, get_request_base_url, parse_json_list


@frappe.whitelist()
def get_student_courses() -> list[dict]:
	user = frappe.session.user
	direct_courses = frappe.get_all("LMS Enrollment", filters={"member": user}, pluck="course")
	enrolled_batches = frappe.get_all("LMS Batch Enrollment", filters={"member": user}, pluck="batch")

	all_course_names = set(direct_courses)
	if enrolled_batches:
		batches = frappe.get_all(
			"LMS Batch",
			filters={"name": ["in", enrolled_batches]},
			fields=["name", "program"],
		)
		programs = [batch.program for batch in batches if batch.program]
		if programs:
			program_courses = frappe.get_all(
				"LMS Program Course",
				filters={"parent": ["in", programs]},
				pluck="course",
			)
			for course in program_courses:
				if course:
					all_course_names.add(course)

		for batch_name in enrolled_batches:
			try:
				batch_doc = frappe.get_doc("LMS Batch", batch_name)
			except Exception:
				continue
			for batch_course in getattr(batch_doc, "courses", []) or []:
				if batch_course.course:
					all_course_names.add(batch_course.course)

	if not all_course_names:
		return []

	return frappe.get_all(
		"LMS Course",
		filters={"name": ["in", list(all_course_names)]},
		fields=[
			"name",
			"title",
			"description",
			"short_introduction",
			"image",
			"category",
			"rating",
			"lessons",
			"enrollments",
		],
	)


@frappe.whitelist()
def get_course_details(course_name: str) -> dict:
	try:
		course = frappe.get_doc("LMS Course", course_name)
	except frappe.DoesNotExistError:
		frappe.throw(f"Course {course_name} not found", frappe.DoesNotExistError)

	course_dict = course.as_dict()
	base_url = get_request_base_url()
	if course_dict.get("description"):
		course_dict["description"] = expand_relative_urls(course_dict["description"], base_url)

	chapters: list[dict] = []
	for row in course.get("chapters", []):
		if not row.chapter:
			continue
		try:
			chapter_doc = frappe.get_doc("Course Chapter", row.chapter)
		except Exception:
			continue

		chapter_dict = {"name": chapter_doc.name, "title": chapter_doc.title, "lessons": []}
		for lesson_row in chapter_doc.get("lessons", []):
			if not lesson_row.lesson:
				continue
			try:
				lesson_doc = frappe.get_doc("Course Lesson", lesson_row.lesson)
			except Exception:
				continue
			chapter_dict["lessons"].append(
				{
					"name": lesson_doc.name,
					"title": lesson_doc.title,
					"youtube": lesson_doc.youtube,
					"quiz_id": lesson_doc.quiz_id,
					"body": lesson_doc.body,
				}
			)
		chapters.append(chapter_dict)

	course_dict["chapters"] = chapters
	return course_dict


@frappe.whitelist()
def get_courses_for_picker(
	search: str = "",
	program_name: str = "",
	course_group: str = "",
	limit: int = 100,
	offset: int = 0,
) -> list:
	course_names = _get_filtered_course_names(
		program_name=program_name,
		course_group=course_group,
	)

	filters: list = []
	if course_names is not None:
		if not course_names:
			return []
		filters.append(["name", "in", course_names])
	if search:
		filters.append(["title", "like", f"%{search}%"])

	return frappe.get_list(
		"LMS Course",
		fields=["name", "title", "published", "lessons", "course_group"],
		filters=filters,
		limit_page_length=limit,
		limit_start=offset,
		order_by="creation desc",
	)


@frappe.whitelist()
def get_all_chapters(
	search: str = "",
	course_name: str = "",
	program_name: str = "",
	course_group: str = "",
	limit: int = 100,
	offset: int = 0,
) -> list:
	chapter_names = _get_filtered_chapter_names(
		course_name=course_name,
		program_name=program_name,
		course_group=course_group,
	)

	filters: list = []
	if chapter_names is not None:
		if not chapter_names:
			return []
		filters.append(["name", "in", chapter_names])
	if search:
		filters.append(["title", "like", f"%{search}%"])

	return frappe.get_list(
		"Course Chapter",
		fields=["name", "title"],
		filters=filters,
		limit_page_length=limit,
		limit_start=offset,
		order_by="creation desc",
	)


@frappe.whitelist()
def get_all_lessons(
	search: str = "",
	chapter_name: str = "",
	course_name: str = "",
	program_name: str = "",
	course_group: str = "",
	limit: int = 100,
	offset: int = 0,
) -> list:
	lesson_names = _get_filtered_lesson_names(
		chapter_name=chapter_name,
		course_name=course_name,
		program_name=program_name,
		course_group=course_group,
	)

	filters: list = []
	if lesson_names is not None:
		if not lesson_names:
			return []
		filters.append(["name", "in", lesson_names])
	if search:
		filters.append(["title", "like", f"%{search}%"])

	return frappe.get_list(
		"Course Lesson",
		fields=["name", "title", "youtube", "quiz_id", "chapter"],
		filters=filters,
		limit_page_length=limit,
		limit_start=offset,
		order_by="creation desc",
	)


def _get_filtered_course_names(
	program_name: str = "",
	course_group: str = "",
) -> list[str] | None:
	candidate_names: list[str] | None = None

	if program_name:
		try:
			program = frappe.get_doc("LMS Program", program_name)
		except frappe.DoesNotExistError:
			return []
		candidate_names = [row.course for row in program.get("program_courses", []) if row.course]

	if course_group:
		group_course_names = frappe.get_all(
			"LMS Course",
			filters={"course_group": course_group},
			pluck="name",
		)
		candidate_names = _intersect_names(candidate_names, group_course_names)

	return candidate_names


def _get_filtered_chapter_names(
	course_name: str = "",
	program_name: str = "",
	course_group: str = "",
) -> list[str] | None:
	course_names = _get_filtered_course_names(
		program_name=program_name,
		course_group=course_group,
	)

	if course_name:
		if course_names is not None and course_name not in course_names:
			return []
		course_names = [course_name]

	if course_names is None:
		return None

	chapter_names: list[str] = []
	for course_name_value in course_names:
		try:
			course = frappe.get_doc("LMS Course", course_name_value)
		except frappe.DoesNotExistError:
			continue
		chapter_names.extend([row.chapter for row in course.get("chapters", []) if row.chapter])

	return chapter_names


def _get_filtered_lesson_names(
	chapter_name: str = "",
	course_name: str = "",
	program_name: str = "",
	course_group: str = "",
) -> list[str] | None:
	chapter_names = _get_filtered_chapter_names(
		course_name=course_name,
		program_name=program_name,
		course_group=course_group,
	)

	if chapter_name:
		if chapter_names is not None and chapter_name not in chapter_names:
			return []
		chapter_names = [chapter_name]

	if chapter_names is None:
		return None

	lesson_names: list[str] = []
	for chapter_name_value in chapter_names:
		try:
			chapter = frappe.get_doc("Course Chapter", chapter_name_value)
		except frappe.DoesNotExistError:
			continue
		lesson_names.extend([row.lesson for row in chapter.get("lessons", []) if row.lesson])

	return lesson_names


def _intersect_names(left: list[str] | None, right: list[str]) -> list[str]:
	if left is None:
		return right

	right_set = set(right)
	return [name for name in left if name in right_set]


@frappe.whitelist()
def get_course_chapters(course_name: str) -> list:
	try:
		course = frappe.get_doc("LMS Course", course_name)
	except frappe.DoesNotExistError:
		frappe.throw(f"Course {course_name} not found", frappe.DoesNotExistError)

	chapters: list[dict] = []
	for row in course.get("chapters", []):
		if not row.chapter:
			continue
		try:
			chapter_doc = frappe.get_doc("Course Chapter", row.chapter)
		except frappe.DoesNotExistError:
			continue
		chapters.append(
			{
				"name": chapter_doc.name,
				"title": chapter_doc.title,
				"lessons": [
					{
						"name": lesson.name,
						"lesson": lesson.lesson,
						"lesson_title": frappe.db.get_value("Course Lesson", lesson.lesson, "title"),
						"idx": lesson.idx,
					}
					for lesson in chapter_doc.get("lessons", [])
					if lesson.lesson
				],
			}
		)

	return chapters


@frappe.whitelist()
def get_course_lesson_details(lesson_name: str) -> dict:
	try:
		lesson = frappe.get_doc("Course Lesson", lesson_name)
	except frappe.DoesNotExistError:
		frappe.throw(f"Lesson {lesson_name} not found", frappe.DoesNotExistError)

	base_url = get_request_base_url()
	chapter_title = frappe.db.get_value("Course Chapter", lesson.chapter, "title")
	course_title = frappe.db.get_value("LMS Course", lesson.course, "title")
	body = lesson.body or ""
	content = lesson.content or ""
	instructor_notes = lesson.instructor_notes or ""
	question = lesson.question or ""

	return {
		"name": lesson.name,
		"title": lesson.title,
		"chapter": lesson.chapter,
		"chapter_title": chapter_title,
		"course": lesson.course,
		"course_title": course_title,
		"youtube": lesson.youtube,
		"quiz_id": lesson.quiz_id,
		"body": expand_relative_urls(body, base_url) if body else "",
		"content": expand_relative_urls(content, base_url) if content else "",
		"instructor_notes": expand_relative_urls(instructor_notes, base_url) if instructor_notes else "",
		"question": expand_relative_urls(question, base_url) if question else "",
	}


@frappe.whitelist()
def update_chapter_order(course_name: str, chapter_names: list | str) -> str:
	parsed_chapter_names = parse_json_list(chapter_names) if isinstance(chapter_names, str) else chapter_names
	course = frappe.get_doc("LMS Course", course_name)
	course.set("chapters", [{"chapter": chapter_name} for chapter_name in parsed_chapter_names])
	course.save(ignore_permissions=True)
	return "Success"


@frappe.whitelist()
def update_lesson_order(chapter_name: str, lesson_names: list | str) -> str:
	parsed_lesson_names = parse_json_list(lesson_names) if isinstance(lesson_names, str) else lesson_names
	chapter = frappe.get_doc("Course Chapter", chapter_name)
	chapter.set("lessons", [{"lesson": lesson_name} for lesson_name in parsed_lesson_names])
	chapter.save(ignore_permissions=True)
	return "Success"


@frappe.whitelist()
def duplicate_course(course_name: str, include_children: bool | str = False) -> str:
	include_children_flag = frappe.utils.cint(include_children)
	old_course = frappe.get_doc("LMS Course", course_name)
	if include_children_flag:
		return duplicate_course_with_children(old_course).name

	new_course = frappe.copy_doc(old_course)
	new_course.title = f"{old_course.title} (Copy)"
	new_course.published = 0
	new_course.insert()
	return new_course.name


def duplicate_course_with_children(old_course):
	new_course = frappe.copy_doc(old_course)
	new_course.title = f"{old_course.title} (Copy)"
	new_course.published = 0

	new_chapters = []
	for row in old_course.get("chapters") or []:
		if not row.chapter:
			continue
		try:
			old_chapter = frappe.get_doc("Course Chapter", row.chapter)
		except frappe.DoesNotExistError:
			continue
		new_chapter = duplicate_chapter_with_children(old_chapter)
		new_chapters.append({"chapter": new_chapter.name})

	new_course.set("chapters", new_chapters)
	new_course.insert()
	return new_course


@frappe.whitelist()
def duplicate_chapter(chapter_name: str, include_children: bool | str = False) -> str:
	include_children_flag = frappe.utils.cint(include_children)
	old_chapter = frappe.get_doc("Course Chapter", chapter_name)
	if include_children_flag:
		return duplicate_chapter_with_children(old_chapter).name

	new_chapter = frappe.copy_doc(old_chapter)
	new_chapter.title = f"{old_chapter.title} (Copy)"
	new_chapter.insert()
	return new_chapter.name


def duplicate_chapter_with_children(old_chapter):
	new_chapter = frappe.copy_doc(old_chapter)
	new_chapter.title = f"{old_chapter.title} (Copy)"

	new_lessons = []
	for row in old_chapter.get("lessons") or []:
		if not row.lesson:
			continue
		try:
			old_lesson = frappe.get_doc("Course Lesson", row.lesson)
		except frappe.DoesNotExistError:
			continue
		new_lesson = frappe.copy_doc(old_lesson)
		new_lesson.title = f"{old_lesson.title} (Copy)"
		new_lesson.insert()
		new_lessons.append({"lesson": new_lesson.name})

	new_chapter.set("lessons", new_lessons)
	new_chapter.insert()
	return new_chapter
