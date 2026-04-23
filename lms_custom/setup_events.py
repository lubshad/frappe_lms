import frappe

def ignore_mandatory_in_setup_wizard(doc, method):
	if getattr(frappe.flags, "in_setup_wizard", False):
		doc.flags.ignore_mandatory = True
