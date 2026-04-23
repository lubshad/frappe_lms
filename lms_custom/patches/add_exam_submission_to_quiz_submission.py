import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields({
		"LMS Quiz Submission": [
			{
				"fieldname": "exam_submission",
				"label": "Exam Submission",
				"fieldtype": "Link",
				"options": "Exam Submission",
				"insert_after": "quiz",
				"read_only": 1,
				"in_list_view": 1,
			}
		]
	})
