import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def execute():
	""" Make 'instructors' field in 'LMS Batch' optional. """
	if not frappe.db.table_exists("LMS Batch"):
		return

	# Use property setter for permanence across migrations
	make_property_setter("LMS Batch", "instructors", "reqd", 0, "Check")
	
	# Update DocField directly as well just in case
	frappe.db.sql("""
		UPDATE `tabDocField`
		SET reqd = 0
		WHERE parent = 'LMS Batch' AND fieldname = 'instructors'
	""")

	frappe.clear_cache(doctype="LMS Batch")
