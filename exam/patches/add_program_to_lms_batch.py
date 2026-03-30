import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute() -> None:
	""" Add 'program' field to 'LMS Batch' DocType. """
	if not frappe.db.table_exists("LMS Batch"):
		return

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
				"in_standard_filter": 1
			}
		]
	}
	create_custom_fields(custom_fields, ignore_validate=True)
