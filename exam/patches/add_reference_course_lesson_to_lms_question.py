import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_fields = {
        "LMS Question": [
            dict(
                fieldname="reference_lesson",
                label="Reference Lesson",
                fieldtype="Link",
                options="Course Lesson",
                insert_after="question",
                description="Optional reference to a Course Lesson for remediation. Useful for directing students to review specific material when they answer incorrectly."
            )
        ]
    }
    
    create_custom_fields(custom_fields)
