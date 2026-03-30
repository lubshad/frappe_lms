import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute() -> None:
    """ Add optional 'course' field to 'LMS Batch Enrollment' DocType. """
    if not frappe.db.table_exists("LMS Batch Enrollment"):
        return

    custom_fields = {
        "LMS Batch Enrollment": [
            {
                "fieldname": "course",
                "fieldtype": "Link",
                "label": "Course",
                "options": "LMS Course",
                "insert_after": "batch",
                "reqd": 0, # Optional
                "in_list_view": 1,
                "in_standard_filter": 1
            }
        ]
    }
    create_custom_fields(custom_fields, ignore_validate=True)
