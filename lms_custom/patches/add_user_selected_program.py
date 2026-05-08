import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


def execute() -> None:
	"""Add selected_program to User for LMS program-scoped exam/course filtering."""
	# Cleanup previous attempt
	frappe.db.delete("Custom Field", {"dt": "User", "fieldname": "exam_tab"})
	frappe.db.delete("Custom Field", {"dt": "User", "fieldname": "exam_section"})

	custom_fields = {
		"User": [
			{
				"fieldname": "selected_program",
				"fieldtype": "Link",
				"label": "Selected Program",
				"options": "LMS Program",
				"insert_after": "education"
			}
		]
	}
	create_custom_fields(custom_fields, ignore_validate=True)

	if frappe.db.has_column("User", "onboarding_status"):
		make_property_setter(
			"User",
			"onboarding_status",
			"insert_after",
			"selected_program",
			"Data",
			for_doctype=False,
		)
