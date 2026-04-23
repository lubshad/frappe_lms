import frappe
from frappe.utils import cint

from lms_custom.api._utils import (
	get_enrolled_course_and_program_names,
	get_exam_section_payloads,
)


@frappe.whitelist()
def get_exam(exam_name: str) -> dict:
	from lms_custom.lms_custom.doctype.exam.exam import get_exam as doc_get_exam

	return doc_get_exam(exam_name)


@frappe.whitelist()
def get_exam_progress(exam_name: str, member: str | None = None) -> dict:
	from lms_custom.lms_custom.doctype.exam.exam import get_exam_progress as doc_get_exam_progress

	return doc_get_exam_progress(exam_name, member)


@frappe.whitelist()
def save_exam_attempt_draft(
	exam_name: str,
	answers: str | dict | None = None,
	current_question: int = 0,
	flagged_questions: str | list | None = None,
	remaining_seconds: int | None = None,
) -> dict:
	from lms_custom.lms_custom.doctype.exam.exam import (
		save_exam_attempt_draft as doc_save_exam_attempt_draft,
	)

	return doc_save_exam_attempt_draft(
		exam_name,
		answers=answers,
		current_question=current_question,
		flagged_questions=flagged_questions,
		remaining_seconds=remaining_seconds,
	)


@frappe.whitelist()
def get_exam_attempt_draft(exam_name: str) -> dict | None:
	from lms_custom.lms_custom.doctype.exam.exam import (
		get_exam_attempt_draft as doc_get_exam_attempt_draft,
	)

	return doc_get_exam_attempt_draft(exam_name)


@frappe.whitelist()
def submit_exam(exam_name: str, all_results: str | dict) -> dict:
	from lms_custom.lms_custom.doctype.exam.exam import submit_exam as doc_submit_exam

	return doc_submit_exam(exam_name, all_results)


@frappe.whitelist()
def get_exam_submissions(limit: int = 100, offset: int = 0) -> list:
	member = frappe.session.user
	submissions_list = frappe.get_all(
		"Exam Submission",
		filters={"member": member},
		fields=[
			"name as submission_id",
			"exam as exam_name",
			"exam_title",
			"total_score",
			"total_max_marks as total_max",
			"percentage",
			"passed",
			"creation as last_submitted_at",
			"report_content as is_report_generated",
		],
		order_by="creation desc",
		limit_page_length=cint(limit),
		limit_start=cint(offset),
	)

	for submission in submissions_list:
		submission["is_report_generated"] = 1 if submission.get("is_report_generated") else 0
		section_submissions = frappe.get_all(
			"Exam Submission Section",
			filters={"parent": submission.submission_id},
			fields=["submission", "quiz", "score", "max_marks", "course_group"],
			order_by="idx asc",
		)
		for section in section_submissions:
			if section.quiz:
				section["section_title"] = frappe.db.get_value("LMS Quiz", section.quiz, "title") or section.quiz
			section["percentage"] = (section.score / section.max_marks * 100) if section.get("max_marks") else 0.0
			section["submitted_at"] = submission.last_submitted_at

		submission["section_submissions"] = section_submissions
		submission["total_sections"] = len(section_submissions)
		submission["completed_sections"] = len([section for section in section_submissions if section.get("submission")])
		exam_info = frappe.db.get_value("Exam", submission.exam_name, ["passing_percentage", "show_results"], as_dict=True)
		if exam_info:
			submission["passing_percentage"] = exam_info.passing_percentage
			submission["show_results"] = exam_info.show_results
		else:
			submission["passing_percentage"] = 0
			submission["show_results"] = 0

	return submissions_list


@frappe.whitelist()
def submit_section(exam_name: str, quiz_name: str, results: str) -> dict:
	if not frappe.db.exists("Exam", exam_name):
		frappe.throw("Exam not found", frappe.DoesNotExistError)

	exam = frappe.get_doc("Exam", exam_name)
	if not any(row.quiz == quiz_name for row in exam.sections):
		frappe.throw(f"Quiz {quiz_name} is not part of this exam")

	from lms.lms.doctype.lms_quiz.lms_quiz import submit_quiz

	lms_result = submit_quiz(quiz=quiz_name, results=results)
	return {"section": quiz_name, "exam_submission": lms_result}


@frappe.whitelist()
def get_exams(search: str = "", limit: int = 50, start: int = 0) -> list:
	filters = {"title": ["like", f"%{search}%"]} if search else {}
	exams = frappe.get_all(
		"Exam",
		filters=filters,
		fields=["name", "title", "passing_percentage", "negative_marking", "total_marks"],
		limit_start=start,
		limit_page_length=limit,
		order_by="creation desc",
	)

	for exam in exams:
		doc = frappe.get_doc("Exam", exam.name)
		exam["sections"] = get_exam_section_payloads(doc)
		exam["section_count"] = len(exam["sections"])

	return exams


@frappe.whitelist()
def get_assigned_exams(search: str = "", limit: int = 50, start: int = 0) -> list:
	user = frappe.session.user
	if user == "Administrator":
		return get_exams(search, limit, start)

	all_course_names, all_program_names = get_enrolled_course_and_program_names(user)
	course_groups = []
	if all_course_names:
		course_groups = frappe.get_all(
			"Course Group Course",
			filters={"course": ["in", list(all_course_names)]},
			pluck="parent",
		)

	filters = {"title": ["like", f"%{search}%"]} if search else {}
	or_filters = []
	exams_with_programs = frappe.get_all("Exam Program", pluck="parent")
	if exams_with_programs:
		or_filters.append(["name", "not in", list(set(exams_with_programs))])
	else:
		or_filters.append(["name", "is", "set"])

	if all_program_names:
		exam_names_by_program = frappe.get_all(
			"Exam Program",
			filters={"program": ["in", list(all_program_names)]},
			pluck="parent",
		)
		if exam_names_by_program:
			or_filters.append(["name", "in", exam_names_by_program])

	if course_groups:
		or_filters.append(["course_group", "in", course_groups])

	exams = frappe.get_all(
		"Exam",
		filters=filters,
		or_filters=or_filters,
		fields=["name", "title", "passing_percentage", "negative_marking", "total_marks"],
		limit_start=cint(start),
		limit_page_length=cint(limit),
		order_by="creation desc",
	)

	for exam in exams:
		doc = frappe.get_doc("Exam", exam.name)
		exam["sections"] = get_exam_section_payloads(doc)
		exam["section_count"] = len(exam["sections"])

	return exams
