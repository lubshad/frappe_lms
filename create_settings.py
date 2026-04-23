import frappe

def execute():
    if not frappe.db.exists("DocType", "LMS Custom Settings"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "LMS Custom Settings",
            "module": "Lms Custom",
            "custom": 0,
            "issingle": 1,
            "fields": [
                {"fieldname": "app_icon", "fieldtype": "Attach Image", "label": "App Icon"},
                {"fieldname": "favicon", "fieldtype": "Attach Image", "label": "Favicon"},
                {"fieldname": "app_text", "fieldtype": "Data", "label": "App Text"},
                {"fieldname": "primary_color", "fieldtype": "Color", "label": "Primary Color"},
                {"fieldname": "secondary_color", "fieldtype": "Color", "label": "Secondary Color"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1},
                {"role": "Administrator", "read": 1, "write": 1, "create": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print("LMS Custom Settings DocType created successfully.")
    else:
        print("DocType already exists.")
