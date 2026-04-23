import frappe
from frappe.utils import cint

from lms_custom.api.courses import duplicate_course_with_children
from lms_custom.api._utils import parse_json_list


@frappe.whitelist()
def update_program_course_order(program_name: str, course_names: list | str) -> str:
	parsed_course_names = parse_json_list(course_names) if isinstance(course_names, str) else course_names
	program = frappe.get_doc("LMS Program", program_name)
	program.set("program_courses", [{"course": course_name} for course_name in parsed_course_names])
	program.save(ignore_permissions=True)
	return "Success"


@frappe.whitelist()
def duplicate_program(program_name: str, include_children: bool | str = False) -> str:
	include_children_flag = cint(include_children)
	old_program = frappe.get_doc("LMS Program", program_name)
	new_program = frappe.copy_doc(old_program)
	new_program.title = f"{old_program.title} (Copy)"
	new_program.published = 0

	if include_children_flag:
		new_courses = []
		for row in old_program.get("program_courses") or []:
			if not row.course:
				continue
			try:
				old_course = frappe.get_doc("LMS Course", row.course)
			except frappe.DoesNotExistError:
				continue
			new_course = duplicate_course_with_children(old_course)
			new_courses.append({"course": new_course.name})
		new_program.set("program_courses", new_courses)

	new_program.insert()
	return new_program.name
