import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute() -> None:
	""" Add 'member_type' field to 'LMS Batch Enrollment' DocType. """
	if not frappe.db.table_exists("LMS Batch Enrollment"):
		return

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
				"in_standard_filter": 1
			}
		]
	}
	create_custom_fields(custom_fields, ignore_validate=True)
