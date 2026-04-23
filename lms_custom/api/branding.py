import frappe

from lms_custom.api._utils import absolute_url, get_allowed_lms_desktop_icons


@frappe.whitelist(allow_guest=True)
def get_app_settings() -> dict:
	doc = frappe.get_single("LMS Custom Settings")
	return {
		"app_icon": absolute_url(doc.get("app_icon")),
		"favicon": absolute_url(doc.get("favicon")),
		"app_text": doc.get("app_text"),
		"app_description": doc.get("app_description"),
		"primary_color": doc.get("primary_color"),
		"secondary_color": doc.get("secondary_color"),
	}


@frappe.whitelist()
def get_allowed_desktop_icons() -> list[dict]:
	return get_allowed_lms_desktop_icons()


@frappe.whitelist(allow_guest=True)
def get_lms_custom_settings() -> dict:
	try:
		settings = frappe.get_doc("LMS Custom Settings", "LMS Custom Settings")
	except frappe.DoesNotExistError:
		return {}

	return {
		"app_icon": absolute_url(settings.get("app_icon")),
		"favicon": absolute_url(settings.get("favicon")),
		"app_text": settings.get("app_text"),
		"primary_color": settings.get("primary_color"),
		"secondary_color": settings.get("secondary_color"),
	}
