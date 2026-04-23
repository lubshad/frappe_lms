import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute() -> None:
	"""Ensure course_group field exists on LMS Course."""
	_ensure_course_group_field_on_lms_course()
	frappe.db.commit()


def _ensure_course_group_field_on_lms_course() -> None:
	if not frappe.db.table_exists("LMS Course"):
		return
	if frappe.db.exists("Custom Field", {"dt": "LMS Course", "fieldname": "course_group"}):
		return
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
