import frappe
from frappe.utils import cint

from lms_custom.api._utils import parse_json_list


@frappe.whitelist()
def get_mentors_list(
	search: str | None = None,
	filters: list | str | None = None,
	limit_start: int | str = 0,
	limit_page_length: int | str = 20,
) -> list[dict]:
	parsed_filters = parse_json_list(filters) if isinstance(filters, str) else (filters or [])
	course_filter = None
	for row in parsed_filters:
		if isinstance(row, list) and len(row) == 3 and row[0] == "course" and row[1] == "=":
			course_filter = row[2]

	conditions = ["member_type = 'Mentor'"]
	args: dict[str, object] = {}
	if search:
		conditions.append("(member_name LIKE %(search)s OR member LIKE %(search)s)")
		args["search"] = f"%{search}%"
	if course_filter:
		conditions.append(
			"member IN (SELECT member FROM `tabLMS Enrollment` WHERE member_type='Mentor' AND course=%(course)s)"
		)
		args["course"] = course_filter

	query = f"""
		SELECT
			member,
			MAX(member_name) as member_name,
			MAX(name) as name,
			AVG(progress) as progress
		FROM `tabLMS Enrollment`
		WHERE {" AND ".join(conditions)}
		GROUP BY member
		ORDER BY MAX(creation) DESC
		LIMIT %(limit)s OFFSET %(offset)s
	"""
	args.update({"limit": cint(limit_page_length), "offset": cint(limit_start)})
	mentors = frappe.db.sql(query, args, as_dict=True)

	if mentors:
		member_ids = [mentor.member for mentor in mentors]
		all_enrollments = frappe.get_all(
			"LMS Enrollment",
			filters={"member": ["in", member_ids], "member_type": "Mentor"},
			fields=["member", "course"],
		)
		member_courses: dict[str, list[dict[str, str]]] = {}
		for enrollment in all_enrollments:
			member_courses.setdefault(enrollment.member, [])
			if enrollment.course:
				member_courses[enrollment.member].append({"course": enrollment.course})

		for mentor in mentors:
			courses = member_courses.get(mentor.member, [])
			mentor.courses = courses
			mentor.course = courses[0]["course"] if courses else None

	return mentors


@frappe.whitelist()
def get_mentors_count(search: str | None = None, filters: list | str | None = None) -> int:
	parsed_filters = parse_json_list(filters) if isinstance(filters, str) else (filters or [])
	course_filter = None
	for row in parsed_filters:
		if isinstance(row, list) and len(row) == 3 and row[0] == "course" and row[1] == "=":
			course_filter = row[2]

	conditions = ["member_type = 'Mentor'"]
	args: dict[str, object] = {}
	if search:
		conditions.append("(member_name LIKE %(search)s OR member LIKE %(search)s)")
		args["search"] = f"%{search}%"
	if course_filter:
		conditions.append(
			"member IN (SELECT member FROM `tabLMS Enrollment` WHERE member_type='Mentor' AND course=%(course)s)"
		)
		args["course"] = course_filter

	query = f"SELECT COUNT(DISTINCT member) FROM `tabLMS Enrollment` WHERE {' AND '.join(conditions)}"
	count = frappe.db.sql(query, args)[0][0]
	return count or 0


@frappe.whitelist()
def get_mentor_detail(member: str) -> dict:
	enrollments = frappe.get_all(
		"LMS Enrollment",
		filters={"member": member, "member_type": "Mentor"},
		fields=["name", "course", "member_name", "progress"],
	)
	if not enrollments:
		member_name = frappe.db.get_value("User", member, "full_name") or member
		return {
			"name": member,
			"member": member,
			"member_name": member_name,
			"courses": [],
			"progress": 0,
			"member_type": "Mentor",
			"course": None,
		}

	response_courses = []
	for enrollment in enrollments:
		if not enrollment.course:
			continue
		title = frappe.db.get_value("LMS Course", enrollment.course, "title") or enrollment.course
		response_courses.append({"name": enrollment.course, "title": title})

	return {
		"name": member,
		"member": member,
		"member_name": enrollments[0].member_name,
		"courses": response_courses,
		"progress": sum([enrollment.progress for enrollment in enrollments]) / len(enrollments)
		if enrollments
		else 0,
		"member_type": "Mentor",
		"course": enrollments[0].course if enrollments else None,
	}


@frappe.whitelist()
def save_mentor_enrollments(member: str, courses: list | str, member_name: str | None = None) -> str:
	parsed_courses = parse_json_list(courses) if isinstance(courses, str) else courses
	existing = frappe.get_all(
		"LMS Enrollment",
		filters={"member": member, "member_type": "Mentor"},
		fields=["name", "course"],
	)
	existing_courses = {row.course: row.name for row in existing}
	target_courses = {course.get("course") for course in parsed_courses if course.get("course")}

	for course_name, enrollment_name in existing_courses.items():
		if course_name not in target_courses:
			frappe.delete_doc("LMS Enrollment", enrollment_name, ignore_permissions=True)

	for course_name in target_courses:
		if course_name in existing_courses:
			continue
		doc = frappe.new_doc("LMS Enrollment")
		doc.member = member
		doc.course = course_name
		doc.member_type = "Mentor"
		if member_name:
			doc.member_name = member_name
		try:
			doc.insert(ignore_permissions=True)
		except Exception as exc:
			frappe.log_error(title="Failed to auto enroll Mentor", message=str(exc))

	return "Success"


@frappe.whitelist()
def delete_mentor(member: str) -> str:
	frappe.has_permission("LMS Enrollment", "delete", throw=True)
	enrollments = frappe.get_all(
		"LMS Enrollment",
		filters={"member": member, "member_type": "Mentor"},
		fields=["name"],
	)
	for enrollment in enrollments:
		frappe.delete_doc("LMS Enrollment", enrollment.name, ignore_permissions=True)
	return "Success"


@frappe.whitelist()
def get_instructors(search: str = "", course: str = "", limit: int = 20, offset: int = 0) -> dict:
	limit = cint(limit)
	offset = cint(offset)
	filters: dict[str, object] = {"member_type": "Mentor"}
	if course:
		filters["course"] = course

	if search:
		matching_users = frappe.get_all(
			"User",
			filters={"name": ["like", f"%{search}%"], "full_name": ["like", f"%{search}%"]},
			pluck="name",
		)
		if not matching_users:
			return {"results": [], "total": 0}
		filters["member"] = ["in", matching_users]

	unique_members = frappe.get_all(
		"LMS Enrollment",
		filters=filters,
		fields=["member"],
		group_by="member",
		limit_page_length=limit,
		limit_start=offset,
		order_by="creation desc",
	)

	where_sql = "WHERE member_type = 'Mentor'"
	params: list[object] = []
	if course:
		where_sql += " AND course = %s"
		params.append(course)
	if search:
		where_sql += " AND (member IN (SELECT name FROM `tabUser` WHERE full_name LIKE %s OR name LIKE %s))"
		params.extend([f"%{search}%", f"%{search}%"])

	total_result = frappe.db.sql(
		f"SELECT COUNT(DISTINCT member) FROM `tabLMS Enrollment` {where_sql}",
		params,
	)
	total_unique = total_result[0][0] if total_result else 0

	results = []
	for member_row in unique_members:
		member_id = member_row.member
		if not member_id:
			continue
		user_info = frappe.db.get_value("User", member_id, ["full_name", "user_image", "email"], as_dict=True)
		instructor = {
			"name": member_id,
			"full_name": user_info.full_name if user_info else member_id,
			"email": user_info.email if user_info else member_id,
			"image": user_info.user_image if user_info else None,
			"courses": [],
		}
		enrollments = frappe.get_all(
			"LMS Enrollment",
			filters={"member": member_id, "member_type": "Mentor"},
			fields=["course"],
		)
		for enrollment in enrollments:
			if not enrollment.course:
				continue
			course_title = frappe.db.get_value("LMS Course", enrollment.course, "title")
			if course_title and not any(course["name"] == enrollment.course for course in instructor["courses"]):
				instructor["courses"].append({"name": enrollment.course, "title": course_title})
		results.append(instructor)

	return {"results": results, "total": total_unique}


@frappe.whitelist()
def bulk_delete_mentors(members: list | str) -> str:
	frappe.has_permission("LMS Enrollment", "delete", throw=True)
	parsed_members = parse_json_list(members) if isinstance(members, str) else members
	if not parsed_members:
		return "Success"

	enrollments = frappe.get_all(
		"LMS Enrollment",
		filters={"member": ["in", parsed_members], "member_type": "Mentor"},
		fields=["name"],
	)
	for enrollment in enrollments:
		frappe.delete_doc("LMS Enrollment", enrollment.name, ignore_permissions=True)
	return "Success"
