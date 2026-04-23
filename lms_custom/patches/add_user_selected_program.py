import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute() -> None:
	# Cleanup previous attempt
	frappe.db.delete("Custom Field", {"dt": "User", "fieldname": "exam_tab"})
	frappe.db.delete("Custom Field", {"dt": "User", "fieldname": "exam_section"})

	custom_fields: dict[str, list[dict[str, any]]] = {
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

	frappe.make_property_setter({
		"doctype": "User",
		"fieldname": "onboarding_status",
		"property": "insert_after",
		"value": "selected_program",
		"property_type": "Data"
	})
