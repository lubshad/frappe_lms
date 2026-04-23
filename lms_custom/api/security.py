import hashlib
import hmac
import time

import frappe


@frappe.whitelist()
def get_csrf_token() -> str:
	return frappe.sessions.get_csrf_token()


@frappe.whitelist(allow_guest=True)
def get_signed_file(file_url: str, expiry: str, signature: str):
	if int(expiry) < time.time():
		frappe.throw("Signed URL has expired", frappe.PermissionError)

	secret = frappe.conf.get("encryption_key") or "secret"
	data = f"{file_url}{expiry}"
	expected_signature = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()

	if not hmac.compare_digest(signature, expected_signature):
		frappe.throw("Invalid signature for this file", frappe.PermissionError)

	try:
		from frappe.utils.file_manager import get_file

		actual_file_url = file_url.split("?")[0]
		fname, fcontent = get_file(actual_file_url)

		frappe.response.filename = fname
		frappe.response.filecontent = fcontent
		frappe.response.type = "binary"
		frappe.response.headers = {"Cache-Control": "public, max-age=86400"}
	except Exception as exc:
		frappe.throw(f"Error reading file {file_url}: {exc}", frappe.DoesNotExistError)
