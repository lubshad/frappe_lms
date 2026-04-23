import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def execute():
	# LMS Quiz Result
	# Change "question" and "answer" fields to "Text Editor"
	# These fields correspond to "Question" and "Users Response" in the UI
	fields = ["question", "answer"]
	for fieldname in fields:
		make_property_setter("LMS Quiz Result", fieldname, "fieldtype", "Text Editor", "Data", for_doctype=False)
	
	frappe.db.updatedb("LMS Quiz Result")
