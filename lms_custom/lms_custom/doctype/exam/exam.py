# Copyright (c) 2026, CoreAxis Solutions and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint


class Exam(Document):
	def validate(self):
		self.validate_sections()
		self.calculate_total_marks()

	def calculate_total_marks(self):
		self.total_marks = sum(row.total_marks or 0 for row in self.sections)

	def validate_sections(self):
		if not self.sections:
			frappe.throw(_("At least one section is required."))

		sequence_seen = set()
		for idx, row in enumerate(self.sections, 1):
			if not row.sequence:
				row.sequence = idx
			if row.sequence in sequence_seen:
				frappe.throw(
					_("Duplicate sequence number {0} in sections").format(row.sequence)
				)
			sequence_seen.add(row.sequence)

		# Sort sections by sequence
		self.sections = sorted(self.sections, key=lambda r: r.sequence)


def _draft_cache_key(exam_name: str, member: str) -> str:
	return f"exam_attempt_draft::{member}::{exam_name}"


def _parse_json_payload(value, default):
	if value is None:
		return default
	if isinstance(value, str):
		value = value.strip()
		if not value:
			return default
		return json.loads(value)
	return value


@frappe.whitelist()
def get_exam(exam_name: str) -> dict:
	"""Return exam structure with section details for the frontend."""
	exam = frappe.get_doc("Exam", exam_name)
	if not exam:
		frappe.throw(_("Exam not found"))

	sections = []
	for row in exam.sections:
		quiz = frappe.db.get_value(
			"LMS Quiz",
			row.quiz,
			["name", "title", "duration", "total_marks", "passing_percentage", "max_attempts", "shuffle_questions"],
			as_dict=True,
		)
		sections.append({
			"section_title": row.section_title or quiz.title,
			"quiz": row.quiz,
			"quiz_title": quiz.title,
			"course_group": row.course_group,
			"course_group_title": row.course_group_title,
			"duration": quiz.duration,
			"total_marks": quiz.total_marks,
			"passing_percentage": quiz.passing_percentage,
			"sequence": row.sequence,
			"mandatory": row.mandatory,
			"max_attempts": quiz.max_attempts,
			"shuffle_questions": quiz.shuffle_questions,
		})

	member = frappe.session.user
	attempt_count = frappe.db.count(
		"Exam Submission", filters={"exam": exam_name, "member": member}
	)

	max_attempts_values = [s["max_attempts"] for s in sections if s.get("max_attempts")]
	if max_attempts_values:
		max_attempts = min(max_attempts_values)
	else:
		max_attempts = 0

	return {
		"name": exam.name,
		"title": exam.title,
		"total_marks": exam.total_marks,
		"passing_percentage": exam.passing_percentage,
		"negative_marking": exam.negative_marking,
		"marks_to_cut": exam.marks_to_cut,
		"show_results": exam.show_results,
		"sections": sections,
		"attempt_count": attempt_count,
		"max_attempts": max_attempts,
	}


@frappe.whitelist()
def get_exam_progress(exam_name: str, member: str = None) -> dict:
	"""Return aggregated progress for an exam — section scores, total score, pass/fail."""
	if not member:
		member = frappe.session.user

	exam = frappe.get_doc("Exam", exam_name)
	if not exam:
		frappe.throw(_("Exam not found"))

	section_results = []
	total_score = 0
	total_max = 0

	for row in exam.sections:
		submissions = frappe.get_all(
			"LMS Quiz Submission",
			filters={"quiz": row.quiz, "member": member},
			fields=["name", "score", "score_out_of", "percentage", "creation"],
			order_by="creation desc",
			limit=1,
		)
		best = submissions[0] if submissions else None

		if best:
			total_score += best.score
			total_max += best.score_out_of

		quiz_title = frappe.db.get_value("LMS Quiz", row.quiz, "title") or row.quiz
		section_results.append({
			"quiz": row.quiz,
			"section_title": row.section_title or quiz_title,
			"course_group": row.course_group,
			"course_group_title": row.course_group_title,
			"submitted": bool(best),
			"submission": best.name if best else None,
			"score": best.score if best else 0,
			"score_out_of": best.score_out_of if best else 0,
			"percentage": best.percentage if best else 0,
			"submitted_at": best.creation if best else None,
		})

	overall_percentage = (total_score / total_max * 100) if total_max else 0
	passed = overall_percentage >= exam.passing_percentage if exam.passing_percentage else False

	return {
		"exam": exam_name,
		"title": exam.title,
		"sections": section_results,
		"total_score": total_score,
		"total_max": total_max,
		"overall_percentage": overall_percentage,
		"passing_percentage": exam.passing_percentage,
		"passed": passed,
		"show_results": exam.show_results,
	}


@frappe.whitelist()
def submit_section(exam_name: str, quiz_name: str, results: str) -> dict:
	"""Submit a single section (quiz) of an exam. Delegates to LMS submit_quiz."""
	if not frappe.db.exists("Exam", exam_name):
		frappe.throw(_("Exam not found"))

	exam = frappe.get_doc("Exam", exam_name)
	quiz_exists = any(row.quiz == quiz_name for row in exam.sections)
	if not quiz_exists:
		frappe.throw(_("Quiz {0} is not part of this exam").format(quiz_name))

	# Delegate to existing LMS quiz submission
	from lms.lms.doctype.lms_quiz.lms_quiz import submit_quiz
	lms_result = submit_quiz(quiz=quiz_name, results=results)

	return {
		"section": quiz_name,
		"exam_submission": lms_result,
	}


@frappe.whitelist()
def submit_exam(exam_name: str, all_results: str | dict) -> dict:
	"""Unified submission for all sections of an exam."""
	if not frappe.db.exists("Exam", exam_name):
		frappe.throw(_("Exam not found"))

	exam = frappe.get_doc("Exam", exam_name)
	results_map = _parse_json_payload(all_results, {})
	member = frappe.session.user

	from lms.lms.doctype.lms_quiz.lms_quiz import submit_quiz

	total_score = 0
	total_max = 0
	sections_summary = []

	for row in exam.sections:
		quiz_results = results_map.get(row.quiz)
		if not quiz_results and row.mandatory:
			frappe.throw(_("Results for mandatory section {0} are missing.").format(row.section_title or row.quiz))

		summary_row = {
			"quiz": row.quiz,
			"course_group": row.course_group,
		}

		if quiz_results:
			# quiz_results should be a list of dicts (the answers)
			lms_result = submit_quiz(quiz=row.quiz, results=json.dumps(quiz_results))
			
			total_score += lms_result["score"]
			total_max += lms_result["score_out_of"]
			
			summary_row.update({
				"submission": lms_result["submission"],
				"score": lms_result["score"],
				"max_marks": lms_result["score_out_of"]
			})
		else:
			# Non-mandatory but missing result
			quiz_max = frappe.db.get_value("LMS Quiz", row.quiz, "total_marks")
			total_max += quiz_max
			summary_row.update({
				"score": 0,
				"max_marks": quiz_max
			})
		
		sections_summary.append(summary_row)

	percentage = (total_score / total_max * 100) if total_max else 0
	passed = percentage >= exam.passing_percentage if exam.passing_percentage else False

	# Create Exam Submission record
	submission = frappe.get_doc({
		"doctype": "Exam Submission",
		"exam": exam_name,
		"member": member,
		"total_score": total_score,
		"total_max_marks": total_max,
		"percentage": percentage,
		"passed": passed,
		"sections": sections_summary
	})
	submission.insert(ignore_permissions=True)

	# Link the individual quiz submissions back to the exam submission
	for row in submission.sections:
		if row.submission:
			frappe.db.set_value("LMS Quiz Submission", row.submission, "exam_submission", submission.name)

	frappe.cache().delete_value(_draft_cache_key(exam_name, member))

	return {
		"name": submission.name,
		"total_score": total_score,
		"total_max_marks": total_max,
		"percentage": percentage,
		"passed": passed,
		"sections": sections_summary
	}


@frappe.whitelist()
def save_exam_attempt_draft(
	exam_name: str,
	answers: str | dict | None = None,
	current_question: int = 0,
	flagged_questions: str | list | None = None,
	remaining_seconds: int | None = None,
) -> dict:
	"""Persist an in-progress exam attempt draft in cache for the current user."""
	if not frappe.db.exists("Exam", exam_name):
		frappe.throw(_("Exam not found"))

	member = frappe.session.user
	parsed_answers = _parse_json_payload(answers, {})
	parsed_flags = _parse_json_payload(flagged_questions, [])

	draft = {
		"exam_name": exam_name,
		"member": member,
		"answers": parsed_answers,
		"current_question": cint(current_question),
		"flagged_questions": parsed_flags,
		"remaining_seconds": None if remaining_seconds in (None, "") else cint(remaining_seconds),
		"modified": frappe.utils.now(),
	}

	frappe.cache().set_value(
		_draft_cache_key(exam_name, member),
		json.dumps(draft),
		expires_in_sec=60 * 60 * 24 * 7,
	)
	return {"saved": True, "modified": draft["modified"]}


@frappe.whitelist()
def get_exam_attempt_draft(exam_name: str) -> dict | None:
	"""Return a saved exam attempt draft for the current user if one exists."""
	if not frappe.db.exists("Exam", exam_name):
		frappe.throw(_("Exam not found"))

	member = frappe.session.user
	cached = frappe.cache().get_value(_draft_cache_key(exam_name, member))
	if not cached:
		return None

	draft = _parse_json_payload(cached, None)
	if not draft:
		return None

	return {
		"exam_name": exam_name,
		"answers": draft.get("answers") or {},
		"current_question": cint(draft.get("current_question") or 0),
		"flagged_questions": draft.get("flagged_questions") or [],
		"remaining_seconds": draft.get("remaining_seconds"),
		"modified": draft.get("modified"),
	}


@frappe.whitelist()
def get_exams_list(limit: int = 20, offset: int = 0, search: str = None) -> list:
	"""Return a list of exams with summarized data for the admin listing."""
	filters = {}
	if search:
		filters["title"] = ["like", f"%{search}%"]

	exams = frappe.get_all(
		"Exam",
		filters=filters,
		fields=["name", "title", "total_marks", "passing_percentage", "negative_marking"],
		order_by="modified desc",
		limit_page_length=limit,
		limit_start=offset,
	)

	for exam in exams:
		# Get section count
		exam["section_count"] = frappe.db.count("Exam Section", {"parent": exam.name})
		
		# Get program titles
		programs = frappe.get_all(
			"Exam Program",
			filters={"parent": exam.name},
			fields=["program"]
		)
		exam["programs"] = [p.program for p in programs]

	return exams
