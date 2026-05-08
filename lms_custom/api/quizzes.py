import json

import frappe
from frappe import _
from frappe.utils import cint, cstr, strip_html
from fuzzywuzzy import fuzz

from lms_custom.api._utils import (
	expand_relative_urls,
	get_enrolled_course_and_program_names,
	get_request_base_url,
	parse_json_list,
)


@frappe.whitelist(allow_guest=True)
def get_quiz_with_questions(quiz_name: str, include_answers: bool | str = False) -> dict:
	include_answers_flag = cint(include_answers)
	if include_answers_flag and frappe.session.user == "Guest":
		include_answers_flag = 0

	try:
		quiz = frappe.get_doc("LMS Quiz", quiz_name)
	except frappe.DoesNotExistError:
		frappe.throw(f"Quiz {quiz_name} not found", frappe.DoesNotExistError)

	quiz_dict = quiz.as_dict()
	if "passing_percentage" in quiz_dict:
		quiz_dict["passing_score"] = quiz_dict["passing_percentage"]

	if "duration" in quiz_dict and quiz_dict["duration"]:
		try:
			minutes = int(quiz_dict["duration"])
			quiz_dict["duration"] = minutes * 60
			quiz_dict["is_time_bound"] = 1 if minutes > 0 else 0
		except (ValueError, TypeError):
			quiz_dict["is_time_bound"] = 0
	else:
		quiz_dict["is_time_bound"] = 0

	questions: list[dict] = []
	base_url = get_request_base_url()
	for row in quiz.get("questions", []):
		if not row.question:
			continue
		try:
			question = frappe.get_doc("LMS Question", row.question)
		except Exception:
			continue

		question_dict = question.as_dict()
		if question_dict.get("question"):
			question_dict["question"] = expand_relative_urls(question_dict["question"], base_url)

		question_dict["options"] = []
		for index in range(1, 5):
			option_text = question_dict.get(f"option_{index}")
			if not option_text:
				continue

			option_dict = {
				"name": f"Option {index}",
				"option": expand_relative_urls(option_text, base_url),
			}
			if include_answers_flag:
				option_dict["is_correct"] = question_dict.get(f"is_correct_{index}")
				option_dict["explanation"] = question_dict.get(f"explanation_{index}")
			question_dict["options"].append(option_dict)

		if not include_answers_flag:
			for index in range(1, 5):
				question_dict.pop(f"possibility_{index}", None)
				question_dict.pop(f"is_correct_{index}", None)
				question_dict.pop(f"explanation_{index}", None)

		if question_dict.get("type") == "Choices":
			question_dict["question_type"] = (
				"Multiple Correct Answer" if question_dict.get("multiple") else "Single Correct Answer"
			)
		else:
			question_dict["question_type"] = question_dict.get("type")

		questions.append(question_dict)

	quiz_dict["questions"] = questions
	return quiz_dict


@frappe.whitelist()
def get_assigned_quizzes(search: str = "", limit: int | str = 50, offset: int | str = 0) -> list[dict]:
	user = frappe.session.user
	if user == "Administrator":
		filters = {"title": ["like", f"%{search}%"]} if search else {}
		return frappe.get_all(
			"LMS Quiz",
			filters=filters,
			fields=["name", "title", "passing_percentage as passing_score", "max_attempts", "duration", "show_answers"],
			limit_page_length=cint(limit),
			limit_start=cint(offset),
			order_by="modified desc",
		)

	all_course_names, _ = get_enrolled_course_and_program_names(user)
	if not all_course_names:
		return []

	all_courses = [course for course in all_course_names if course]
	if not all_courses:
		return []

	lesson_info = frappe.get_all(
		"Course Lesson",
		filters={"course": ["in", all_courses]},
		fields=["name", "quiz_id"],
	)
	all_lessons = [lesson.name for lesson in lesson_info if lesson.name]
	linked_quiz_ids = [lesson.quiz_id for lesson in lesson_info if lesson.quiz_id]

	filters = {"title": ["like", f"%{search}%"]} if search else {}
	or_filters = [["course", "in", all_courses]]
	if all_lessons:
		or_filters.append(["lesson", "in", all_lessons])
	if linked_quiz_ids:
		or_filters.append(["name", "in", linked_quiz_ids])

	return frappe.get_all(
		"LMS Quiz",
		filters=filters,
		or_filters=or_filters,
		fields=["name", "title", "passing_percentage as passing_score", "max_attempts", "duration", "show_answers"],
		limit_page_length=cint(limit),
		limit_start=cint(offset),
		order_by="modified desc",
	)


@frappe.whitelist()
def get_quiz_details(quiz_name: str) -> dict:
	try:
		quiz = frappe.get_doc("LMS Quiz", quiz_name)
	except frappe.DoesNotExistError:
		frappe.throw(f"Quiz {quiz_name} not found", frappe.DoesNotExistError)

	quiz_data = quiz.as_dict()
	for question_row in quiz_data.get("questions", []):
		if question_row.get("question"):
			question_row["question_text"] = frappe.db.get_value(
				"LMS Question",
				question_row["question"],
				"question",
			) or ""
	return quiz_data


@frappe.whitelist()
def get_all_questions(search: str = "", limit: int = 100, offset: int = 0) -> list:
	filters: list = []
	if search:
		filters.append(["question", "like", f"%{search}%"])

	return frappe.get_list(
		"LMS Question",
		fields=["name", "question", "type"],
		filters=filters,
		limit_page_length=limit,
		limit_start=offset,
		order_by="creation desc",
	)


@frappe.whitelist()
def get_question_details(question: str) -> dict:
	try:
		doc = frappe.get_doc("LMS Question", question)
	except frappe.DoesNotExistError:
		frappe.throw(f"Question {question} not found", frappe.DoesNotExistError)

	question_dict = doc.as_dict()
	base_url = get_request_base_url()
	for field in [
		"question",
		"option_1",
		"option_2",
		"option_3",
		"option_4",
		"explanation_1",
		"explanation_2",
		"explanation_3",
		"explanation_4",
		"possibility_1",
		"possibility_2",
		"possibility_3",
		"possibility_4",
	]:
		if question_dict.get(field):
			question_dict[field] = expand_relative_urls(question_dict[field], base_url)
	return question_dict


@frappe.whitelist()
def delete_question(question: str) -> None:
	if not question or not question.strip():
		frappe.throw(_("Question is required"))

	question_name = question.strip()
	if not frappe.db.exists("LMS Question", question_name):
		frappe.throw(
			_("Question {0} not found").format(frappe.bold(question_name)),
			frappe.DoesNotExistError,
		)

	linked_rows = frappe.get_all(
		"LMS Quiz Question",
		filters={"question": question_name},
		fields=["parent"],
		limit_page_length=0,
	)
	linked_quiz_names = sorted({row.parent for row in linked_rows if row.parent})
	if linked_quiz_names:
		quiz_titles = frappe.get_all(
			"LMS Quiz",
			filters={"name": ["in", linked_quiz_names]},
			fields=["name", "title"],
			limit_page_length=0,
		)
		title_by_name = {quiz.name: quiz.title for quiz in quiz_titles}
		linked_quiz_labels = [title_by_name.get(name) or name for name in linked_quiz_names]
		preview = ", ".join(linked_quiz_labels[:3])
		if len(linked_quiz_labels) > 3:
			preview = _("{0}, and {1} more").format(preview, len(linked_quiz_labels) - 3)

		frappe.throw(
			_(
				"This question is used in {0} quiz(es): {1}. "
				"Remove it from those quizzes before deleting it."
			).format(
				len(linked_quiz_labels),
				preview,
			)
		)

	frappe.delete_doc("LMS Question", question_name)
	frappe.db.commit()


@frappe.whitelist()
def get_quiz_info(quiz_name: str) -> dict:
	quiz = frappe.get_doc("LMS Quiz", quiz_name)
	member = frappe.session.user
	attempt_count = frappe.db.count("LMS Quiz Submission", filters={"quiz": quiz_name, "member": member})
	duration_seconds = (int(quiz.duration) if quiz.duration else 0) * 60
	return {
		"name": quiz.name,
		"title": quiz.title,
		"passing_score": quiz.passing_percentage,
		"max_attempts": quiz.max_attempts,
		"show_answers": quiz.show_answers,
		"is_time_bound": 1 if duration_seconds > 0 else 0,
		"duration": duration_seconds,
		"attempt_count": attempt_count,
	}


@frappe.whitelist()
def submit_quiz_result(quiz_name: str, results: list | str | None = None) -> dict:
	if not results:
		frappe.throw("Results are required for submission")
	parsed_results = parse_json_list(results) if isinstance(results, str) else results
	return custom_submit_quiz(quiz=quiz_name, results=parsed_results)


def custom_submit_quiz(quiz: str, results: list):
	from lms.lms.doctype.lms_quiz.lms_quiz import create_submission, save_progress_after_quiz

	quiz_details = frappe.db.get_value(
		"LMS Quiz",
		quiz,
		[
			"name",
			"total_marks",
			"passing_percentage",
			"lesson",
			"course",
			"enable_negative_marking",
			"marks_to_cut",
		],
		as_dict=1,
	)

	data = custom_process_results(results, quiz_details)
	processed_results = data["results"]
	score = data["score"]
	is_open_ended = data["is_open_ended"]
	score_out_of = quiz_details.total_marks
	percentage = (score / score_out_of) * 100 if score_out_of else 0
	submission = create_submission(quiz, processed_results, score_out_of, quiz_details.passing_percentage)
	save_progress_after_quiz(quiz_details, percentage)

	return {
		"score": score,
		"score_out_of": score_out_of,
		"submission": submission.name,
		"pass": percentage >= quiz_details.passing_percentage,
		"percentage": percentage,
		"is_open_ended": is_open_ended,
	}


def custom_process_results(results: list, quiz_details: dict):
	score = 0
	is_open_ended = False

	for result in results:
		question_details = frappe.db.get_value(
			"LMS Quiz Question",
			{"parent": quiz_details.name, "question": result["question_name"]},
			["question", "marks", "question_detail", "type"],
			as_dict=1,
		)
		if not question_details:
			continue

		result["question_name"] = question_details.question
		result["question"] = question_details.question_detail
		result["marks_out_of"] = question_details.marks

		if question_details.type != "Open Ended":
			correct = custom_verify_answer(question_details.question, result["answer"])
			if isinstance(result["answer"], list):
				result["answer"] = ", ".join(result["answer"])

			if correct:
				result["marks"] = question_details.marks
			else:
				result["marks"] = -quiz_details.marks_to_cut if quiz_details.enable_negative_marking else 0

			score += result["marks"]
			result["is_correct"] = 1 if correct else 0
		else:
			is_open_ended = True
			result["is_correct"] = 0
			if isinstance(result["answer"], list):
				result["answer"] = result["answer"][0]

	return {"results": results, "score": score, "is_open_ended": is_open_ended}


def custom_verify_answer(question: str, answer: list):
	question_details = custom_get_question_details(question)
	if not question_details:
		return False

	if question_details.get("type") == "User Input":
		ans_str = answer[0] if answer else ""
		return custom_check_input_answers(question, ans_str)

	clean_answers = [strip_html(item or "").strip() for item in answer]
	if question_details.multiple:
		for num in range(1, 5):
			option_text = strip_html(question_details.get(f"option_{num}") or "").strip()
			if option_text and option_text in clean_answers:
				correct = question_details.get(f"is_correct_{num}")
				if not correct:
					return False
			if question_details.get(f"is_correct_{num}") and option_text not in clean_answers:
				return False
		return True

	correct = False
	for num in range(1, 5):
		option_text = strip_html(question_details.get(f"option_{num}") or "").strip()
		if option_text and option_text in clean_answers:
			correct = question_details.get(f"is_correct_{num}")
	return correct


def custom_get_question_details(question: str):
	fields = ["multiple", "type"]
	for num in range(1, 5):
		fields.append(f"option_{cstr(num)}")
		fields.append(f"is_correct_{cstr(num)}")
		fields.append(f"possibility_{cstr(num)}")

	return frappe.db.get_value("LMS Question", question, fields, as_dict=1)


def custom_check_input_answers(question: str, answer: str):
	fields = [f"possibility_{num}" for num in range(1, 5)]
	question_details = frappe.db.get_value("LMS Question", question, fields, as_dict=1)
	if not question_details:
		return 0

	clean_answer = strip_html(answer or "").strip().lower()
	for num in range(1, 5):
		current_possibility = question_details.get(f"possibility_{num}")
		if not current_possibility:
			continue
		clean_possibility = strip_html(current_possibility).strip().lower()
		if clean_possibility and fuzz.token_sort_ratio(clean_possibility, clean_answer) > 85:
			return 1
	return 0


@frappe.whitelist()
def get_quiz_submissions(quiz_name: str | None = None, limit: int | str = 20):
	filters = {"member": frappe.session.user}
	if quiz_name:
		filters["quiz"] = quiz_name
	return frappe.get_list(
		"LMS Quiz Submission",
		filters=filters,
		fields=["name", "quiz", "quiz_title", "score", "score_out_of", "percentage", "creation"],
		limit=cint(limit),
		order_by="creation desc",
	)


@frappe.whitelist()
def update_quiz_question_order(quiz_name: str, question_names: list | str) -> str:
	parsed_question_names = parse_json_list(question_names) if isinstance(question_names, str) else question_names
	quiz = frappe.get_doc("LMS Quiz", quiz_name)
	quiz.set("questions", [{"question": name} for name in parsed_question_names])
	quiz.save(ignore_permissions=True)
	return "Success"


@frappe.whitelist()
def get_quizzes_list(
	search: str = "",
	filters: str | list | None = None,
	limit: int = 20,
	offset: int = 0,
	order_by: str = "creation desc",
) -> list:
	parsed_filters = parse_json_list(filters) if isinstance(filters, str) else (filters or [])
	if search:
		parsed_filters.append(["title", "like", f"%{search}%"])

	quizzes = frappe.get_all(
		"LMS Quiz",
		filters=parsed_filters,
		fields=["name", "title", "passing_percentage", "total_marks", "duration"],
		limit_page_length=int(limit),
		limit_start=int(offset),
		order_by=order_by,
	)
	for quiz in quizzes:
		quiz["question_count"] = frappe.db.count("LMS Quiz Question", {"parent": quiz.name})
	return quizzes
