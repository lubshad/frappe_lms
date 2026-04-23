import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute() -> None:
	"""Add mandatory course_group field to LMS Question."""
	if not frappe.db.table_exists("LMS Question"):
		return
	if frappe.db.exists("Custom Field", {"dt": "LMS Question", "fieldname": "course_group"}):
		return
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
	frappe.db.commit()
