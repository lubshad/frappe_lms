import hashlib
import hmac
import json
import re
import time
from typing import Any

import frappe
from frappe import _
from frappe.boot import get_bootinfo
from frappe.desk.doctype.desktop_icon.desktop_icon import get_desktop_icons
from frappe.utils import cint, cstr, get_url


def absolute_url(path: str | None) -> str | None:
	if not path:
		return None
	return get_url(path)


def get_request_base_url() -> str:
	base_url = get_url()
	request = getattr(frappe.local, "request", None)
	if request and request.host:
		scheme = request.scheme or "http"
		base_url = f"{scheme}://{request.host}"
	return base_url.rstrip("/")


def parse_json_value(value: Any, fallback: Any = None) -> Any:
	if isinstance(value, str):
		stripped = value.strip()
		if not stripped:
			return fallback
		return json.loads(stripped)
	return value if value is not None else fallback


def parse_json_list(value: list | str | None) -> list:
	parsed = parse_json_value(value, [])
	return parsed if isinstance(parsed, list) else []


def get_enrolled_course_and_program_names(user: str) -> tuple[set[str], set[str]]:
	direct_courses = set(
		frappe.get_all(
			"LMS Enrollment",
			filters={"member": user},
			pluck="course",
		)
	)
	enrolled_batches = frappe.get_all(
		"LMS Batch Enrollment",
		filters={"member": user},
		pluck="batch",
	)
	program_names: set[str] = set()
	course_names = {course for course in direct_courses if course}

	if enrolled_batches:
		batches = frappe.get_all(
			"LMS Batch",
			filters={"name": ["in", enrolled_batches]},
			fields=["name", "program"],
		)
		for batch in batches:
			if batch.program:
				program_names.add(batch.program)

		if program_names:
			program_courses = frappe.get_all(
				"LMS Program Course",
				filters={"parent": ["in", list(program_names)]},
				pluck="course",
			)
			course_names.update({course for course in program_courses if course})

		for batch_name in enrolled_batches:
			try:
				batch_doc = frappe.get_doc("LMS Batch", batch_name)
			except frappe.DoesNotExistError:
				continue

			for row in getattr(batch_doc, "courses", []) or []:
				if row.course:
					course_names.add(row.course)

	selected_program = frappe.db.get_value("User", user, "selected_program")
	if selected_program:
		program_names.add(selected_program)
		program_courses = frappe.get_all(
			"LMS Program Course",
			filters={"parent": selected_program},
			pluck="course",
		)
		course_names.update({course for course in program_courses if course})

	return course_names, program_names


def get_exam_section_payloads(doc: Any) -> list[dict[str, Any]]:
	sections: list[dict[str, Any]] = []
	for row in doc.sections:
		quiz = frappe.db.get_value(
			"LMS Quiz",
			row.quiz,
			["duration", "total_marks", "max_attempts", "shuffle_questions"],
			as_dict=True,
		)
		sections.append(
			{
				"quiz": row.quiz,
				"quiz_title": row.quiz_title,
				"section_title": row.section_title,
				"course_group": row.course_group,
				"course_group_title": row.course_group_title,
				"duration": quiz.duration if quiz else 0,
				"total_marks": quiz.total_marks if quiz else 0,
				"passing_percentage": row.passing_percentage,
				"sequence": row.sequence,
				"mandatory": row.mandatory,
				"max_attempts": quiz.max_attempts if quiz else 1,
				"shuffle_questions": quiz.shuffle_questions if quiz else 0,
			}
		)

	return sorted(sections, key=lambda section: section["sequence"])


def normalize_workspace_item(item: dict[str, Any]) -> dict[str, Any]:
	return {
		"label": item.get("label"),
		"link_type": item.get("link_type"),
		"link_to": item.get("link_to"),
		"icon": item.get("icon"),
		"type": item.get("type"),
		"child": cint(item.get("child")),
	}


def get_workspace_items(sidebar_name: str | None) -> list[dict[str, Any]]:
	if not sidebar_name or not frappe.db.exists("Workspace Sidebar", sidebar_name):
		return []

	sidebar = frappe.get_doc("Workspace Sidebar", sidebar_name)
	return [
		normalize_workspace_item(item.as_dict() if hasattr(item, "as_dict") else item)
		for item in (sidebar.get("items") or [])
	]


def get_allowed_lms_desktop_icons() -> list[dict[str, Any]]:
	bootinfo = get_bootinfo()
	permitted_icons = get_desktop_icons(user=frappe.session.user, bootinfo=bootinfo)

	allowed_icons: list[dict[str, Any]] = []
	for icon in permitted_icons:
		icon_name = cstr(icon.get("name"))
		sidebar_name = cstr(icon.get("sidebar") or icon.get("link_to")) or None
		if (
			icon.get("app") != "lms_custom"
			or cint(icon.get("hidden")) == 1
			or icon_name == "Settings"
			or sidebar_name == "Settings"
		):
			continue

		allowed_icons.append(
			{
				"name": icon.get("name"),
				"label": icon.get("label"),
				"bg_color": icon.get("bg_color"),
				"icon_type": icon.get("icon_type"),
				"logo_url": absolute_url(icon.get("logo_url") or icon.get("icon_image")),
				"link_type": icon.get("link_type"),
				"link_to": icon.get("link_to"),
				"sidebar": sidebar_name,
				"workspace_items": get_workspace_items(sidebar_name),
			}
		)

	return allowed_icons


def generate_signed_url(file_path: str, base_url: str | None = None) -> str:
	expires_at = int(time.time() + (7 * 24 * 60 * 60))
	secret = frappe.conf.get("encryption_key") or "secret"
	data = f"{file_path}{expires_at}"
	signature = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
	root_url = (base_url or get_request_base_url()).rstrip("/")
	return (
		f"{root_url}/api/method/lms_custom.api.security.get_signed_file"
		f"?file_url={file_path}&expiry={expires_at}&signature={signature}"
	)


def expand_relative_urls(html_content: str, base_url: str | None = None) -> str:
	if not html_content:
		return html_content

	root_url = (base_url or get_request_base_url()).rstrip("/")

	def _replace(match: re.Match[str]) -> str:
		prefix = match.group(1)
		quote = match.group(2)
		path = match.group(3)
		if path.startswith("/") and not path.startswith("//"):
			return f'{prefix}{quote}{generate_signed_url(path, root_url)}{quote}'
		return match.group(0)

	return re.sub(r'(\b(?:src|href)=)(["\'])(/.*?)\2', _replace, html_content)
