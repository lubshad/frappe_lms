import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
	frappe.reload_doc("lms", "doctype", "lms_question")
	
	if not frappe.db.exists("Custom Field", "LMS Question-marks"):
		create_custom_field("LMS Question", {
			"fieldname": "marks",
			"label": "Marks",
			"fieldtype": "Int",
			"insert_after": "type",
			"default": "1",
			"non_negative": 1
		})
