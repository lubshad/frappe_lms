import frappe


def execute():
	"""Grant Moderator role permissions to exam app doctypes."""
	give_moderator_permissions()


def give_moderator_permissions():
	"""Add Moderator role permissions to Course Group and related doctypes."""
	doctypes_permissions = {
		"Course Group": {
			"read": 1,
			"write": 1,
			"create": 1,
			"delete": 1,
			"email": 1,
			"export": 1,
			"print": 1,
			"report": 1,
			"share": 1,
		},
		"Course Group Course": {
			"read": 1,
			"write": 1,
			"create": 1,
			"delete": 1,
		},
		"LMS Program Quiz": {
			"read": 1,
			"write": 1,
			"create": 1,
			"delete": 1,
		},
	}

	for doctype, permissions in doctypes_permissions.items():
		if frappe.db.exists("DocType", doctype):
			# Check if permission already exists
			if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": "Moderator"}):
				doc = frappe.new_doc("Custom DocPerm")
				permissions["doctype"] = "Custom DocPerm"
				permissions["parent"] = doctype
				permissions["role"] = "Moderator"
				permissions["permlevel"] = 0
				doc.update(permissions)
				doc.save()
				frappe.logger().info(f"Added Moderator permissions to {doctype}")
		else:
			frappe.logger().warning(f"DocType {doctype} not found")

	frappe.clear_cache()
