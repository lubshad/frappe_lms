import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def execute():
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
		"possibility_3", "possibility_4"
	]
	for fieldname in fields:
		make_property_setter("LMS Question", fieldname, "fieldtype", "Text Editor", "Small Text", for_doctype=False)
	
	frappe.db.updatedb("LMS Question")
