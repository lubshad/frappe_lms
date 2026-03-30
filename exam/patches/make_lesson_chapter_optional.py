import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def execute():
	""" Make 'chapter' field in 'Course Lesson' optional to allow unassigning lessons from chapters. """
	if not frappe.db.table_exists("Course Lesson"):
		return

	# Use property setter for permanence across migrations
	make_property_setter("Course Lesson", "chapter", "reqd", 0, "Check")
	
	# Update DocField directly as well just in case
	frappe.db.sql("""
		UPDATE `tabDocField`
		SET reqd = 0
		WHERE parent = 'Course Lesson' AND fieldname = 'chapter'
	""")

	frappe.clear_cache(doctype="Course Lesson")
