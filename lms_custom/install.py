import frappe
import json
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from lms_custom.patches.add_user_selected_program import execute as add_user_selected_program


def after_install() -> None:
	"""Apply all exam app customizations on fresh install."""
	_add_reference_lesson_to_lms_question()

	_make_instructor_optional_in_batch()
	_add_program_to_lms_batch()
	_change_lms_question_field_types()
	_change_lms_quiz_result_field_types()
	_unhide_lesson_youtube_field()
	_move_lesson_video_urls_to_youtube_field()
	_make_lesson_chapter_optional()
	_add_member_type_to_lms_batch_enrollment()
	_add_course_to_lms_batch_enrollment()
	_add_course_to_lms_batch_enrollment()
	_add_course_group_to_lms_course()
	_add_course_group_to_lms_question()
	add_user_selected_program()
	_setup_assistant_prompts()
	frappe.db.commit()


def _setup_assistant_prompts() -> None:
	"""Create or update the context prompt for LMS hierarchies in frappe_assistant_core."""
	if not frappe.db.table_exists("Prompt Template"):
		return

	prompt_id = "lms_hierarchy_context"
	template_content = """# LMS Structure Knowledge

The system uses two distinct hierarchies for organizing educational content. Use this guide to resolve ambiguity in user requests:

### 1. Academic Hierarchy (Standard)
Used for degree-style programs where a Program contains multiple Courses.
- **Program** (`LMS Program`): Top-level degree/diploma.
- **Course** (`LMS Course`): Specific module within the Program.
- **Chapter** (`Course Chapter`): Section within a Course.
- **Lesson** (`Course Lesson`): Individual learning unit.

### 2. Professional/Specialized Hierarchy
Used for certificate courses where the "Program" is the actual course and "Courses" are treated as "Subjects".
- **Course** (Stored as `LMS Program`): The main offering.
- **Subject** (Stored as `LMS Course`): Specific topic within that top-level program.
- **Chapter** (`Course Chapter`): Section within a Subject.
- **Lesson** (`Course Lesson`): Individual learning unit.

### Navigation Rules
- When a user asks about "Subjects" within a "Course", refer to Hierarchy #2.
- When a user asks about "Courses" within a "Program", refer to Hierarchy #1.
- "Chapters" and "Lessons" are always the bottom levels in both hierarchies."""

	# Update or insert the prompt template
	try:
		name = frappe.db.get_value("Prompt Template", {"prompt_id": prompt_id}, "name")
		
		if name:
			doc = frappe.get_doc("Prompt Template", name)
			doc.template_content = template_content
			doc.save(ignore_permissions=True)
		else:
			doc = frappe.get_doc({
				"doctype": "Prompt Template",
				"prompt_id": prompt_id,
				"title": "LMS Content Hierarchy Guide",
				"description": "Explains the two types of content hierarchies used in the LMS (Academic vs. Professional).",
				"template_content": template_content,
				"status": "Published",
				"visibility": "Public",
				"category": "documentation"
			})
			doc.insert(ignore_permissions=True)
	except Exception as e:
		frappe.log_error(f"Failed to setup assistant prompts: {str(e)}")


def _add_reference_lesson_to_lms_question() -> None:
	"""Add reference_lesson custom field to LMS Question."""
	custom_fields = {
		"LMS Question": [
			dict(
				fieldname="reference_lesson",
				label="Reference Lesson",
				fieldtype="Link",
				options="Course Lesson",
				insert_after="question",
				description="Optional reference to a Course Lesson for remediation. Useful for directing students to review specific material when they answer incorrectly.",
			)
		]
	}
	create_custom_fields(custom_fields)





def _change_lms_question_field_types() -> None:
	"""Change LMS Question and LMS Option fields to Text Editor."""
	# LMS Option
	make_property_setter("LMS Option", "option", "fieldtype", "Text Editor", "Data", for_doctype=False)
	frappe.db.updatedb("LMS Option")

	# LMS Question
	fields = [
		"option_1", "explanation_1",
		"option_2", "explanation_2",
		"option_3", "explanation_3",
		"option_4", "explanation_4",
		"possibility_1", "possibility_2",
		"possibility_3", "possibility_4",
	]
	for fieldname in fields:
		make_property_setter("LMS Question", fieldname, "fieldtype", "Text Editor", "Small Text", for_doctype=False)

	frappe.db.updatedb("LMS Question")


def _change_lms_quiz_result_field_types() -> None:
	"""Change LMS Quiz Result question and answer fields to Text Editor."""
	fields = ["question", "answer"]
	for fieldname in fields:
		make_property_setter("LMS Quiz Result", fieldname, "fieldtype", "Text Editor", "Data", for_doctype=False)

	frappe.db.updatedb("LMS Quiz Result")


def _unhide_lesson_youtube_field() -> None:
	"""Unhide the section break in Course Lesson to show YouTube URL and Quiz ID fields."""
	frappe.reload_doc("lms", "doctype", "course_lesson")
	frappe.db.set_value(
		"DocField",
		{"parent": "Course Lesson", "fieldname": "section_break_6"},
		"hidden",
		0,
	)
	frappe.clear_cache(doctype="Course Lesson")


def _move_lesson_video_urls_to_youtube_field() -> None:
	"""Move lesson video URLs from content into the dedicated YouTube Video URL field."""
	lessons = frappe.get_all(
		"Course Lesson",
		filters={"content": ["!=", ""]},
		fields=["name", "content", "youtube"],
		limit=0,
	)

	for lesson in lessons:
		content = (lesson.content or "").strip()
		if not content:
			continue

		video_url = _extract_video_url_from_lesson_content(content=content)
		if not video_url:
			continue

		updates: dict[str, str] = {}
		if not (lesson.youtube or "").strip():
			updates["youtube"] = video_url

		if _should_clear_lesson_content(content=content):
			updates["content"] = ""

		if updates:
			frappe.db.set_value("Course Lesson", lesson.name, updates, update_modified=False)


def _extract_video_url_from_lesson_content(content: str) -> str | None:
	"""Extract a usable video URL from raw lesson content or editor JSON blocks."""
	if content.startswith(("http://", "https://")):
		return content

	try:
		payload = json.loads(content)
	except json.JSONDecodeError:
		return None

	for block in payload.get("blocks", []):
		if block.get("type") != "embed":
			continue

		data = block.get("data") or {}
		for key in ("source", "url"):
			value = data.get(key)
			if isinstance(value, str) and value.startswith(("http://", "https://")):
				return value

	return None


def _should_clear_lesson_content(content: str) -> bool:
	"""Clear content only when it contains nothing except the video payload."""
	if content.startswith(("http://", "https://")):
		return True

	try:
		payload = json.loads(content)
	except json.JSONDecodeError:
		return False

	blocks = payload.get("blocks", [])
	return len(blocks) == 1 and blocks[0].get("type") == "embed"


def _make_instructor_optional_in_batch() -> None:
	"""Set instructors field as optional in LMS Batch."""
	make_property_setter(
		"LMS Batch", "instructors", "reqd", 0, "Check", for_doctype=False
	)


def _add_program_to_lms_batch() -> None:
	"""Add program custom field to LMS Batch."""
	custom_fields = {
		"LMS Batch": [
			{
				"fieldname": "program",
				"fieldtype": "Link",
				"label": "Program",
				"options": "LMS Program",
				"reqd": 1,
				"insert_after": "title",
				"in_list_view": 1,
				"in_standard_filter": 1,
			}
		]
	}
	create_custom_fields(custom_fields, ignore_validate=True)

def _make_lesson_chapter_optional() -> None:
	"""Set chapter field as optional in Course Lesson."""
	make_property_setter(
		"Course Lesson", "chapter", "reqd", 0, "Check", for_doctype=False
	)


def _add_member_type_to_lms_batch_enrollment() -> None:
	"""Add member_type custom field to LMS Batch Enrollment."""
	custom_fields = {
		"LMS Batch Enrollment": [
			{
				"fieldname": "member_type",
				"fieldtype": "Select",
				"label": "Member Type",
				"options": "\nStudent\nMentor\nStaff",
				"default": "Student",
				"insert_after": "member",
				"in_list_view": 1,
				"in_standard_filter": 1,
			}
		]
	}
	create_custom_fields(custom_fields, ignore_validate=True)


def _add_course_group_to_lms_question() -> None:
	"""Add mandatory course_group field to LMS Question."""
	custom_fields = {
		"LMS Question": [
			{
				"fieldname": "course_group",
				"fieldtype": "Link",
				"label": "Course Group",
				"options": "Course Group",
				"reqd": 1,
				"insert_after": "reference_lesson",
				"in_list_view": 1,
				"in_standard_filter": 1,
			}
		]
	}
	create_custom_fields(custom_fields, ignore_validate=True)


def _add_course_group_to_lms_course() -> None:
	"""Add mandatory course_group field to LMS Course."""
	custom_fields = {
		"LMS Course": [
			{
				"fieldname": "course_group",
				"fieldtype": "Link",
				"label": "Course Group",
				"options": "Course Group",
				"reqd": 1,
				"insert_after": "title",
				"in_list_view": 1,
				"in_standard_filter": 1,
			}
		]
	}
	create_custom_fields(custom_fields, ignore_validate=True)




def _add_course_to_lms_batch_enrollment() -> None:
	"""Add course custom field to LMS Batch Enrollment."""
	custom_fields = {
		"LMS Batch Enrollment": [
			{
				"fieldname": "course",
				"fieldtype": "Link",
				"label": "Course",
				"options": "LMS Course",
				"insert_after": "batch",
				"reqd": 0,
				"in_list_view": 1,
				"in_standard_filter": 1,
			}
		]
	}
	create_custom_fields(custom_fields, ignore_validate=True)



