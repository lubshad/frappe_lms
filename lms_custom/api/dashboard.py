import frappe


@frappe.whitelist()
def get_dashboard_stats() -> dict:
	counts: dict[str, int] = {
		"programs": frappe.db.count("LMS Program"),
		"courses": frappe.db.count("LMS Course"),
		"chapters": frappe.db.count("Course Chapter"),
		"lessons": frappe.db.count("Course Lesson"),
		"questions": frappe.db.count("LMS Question"),
		"quizzes": frappe.db.count("LMS Quiz"),
		"exams": frappe.db.count("Exam"),
		"exam_submissions": frappe.db.count("Exam Submission"),
		"students": frappe.db.count("LMS Batch Enrollment"),
		"batches": frappe.db.count("LMS Batch"),
		"live_classes": frappe.db.count("LMS Live Class"),
		"instructors": frappe.db.count("LMS Batch Enrollment", {"member_type": "Instructor"}),
	}
	recent_submissions = frappe.get_all(
		"Exam Submission",
		fields=[
			"name",
			"member",
			"member_name",
			"exam",
			"exam_title",
			"total_score",
			"total_max_marks",
			"percentage",
			"passed",
			"creation",
		],
		order_by="creation desc",
		limit_page_length=5,
	)
	return {
		"counts": counts,
		"recent_submissions": recent_submissions,
		"pass_count": frappe.db.count("Exam Submission", {"passed": 1}),
		"fail_count": frappe.db.count("Exam Submission", {"passed": 0}),
	}


@frappe.whitelist()
def get_student_dashboard_metrics() -> dict:
	user = frappe.session.user
	submissions = frappe.get_all(
		"LMS Quiz Submission",
		filters={"member": user},
		fields=["percentage"],
	)
	total_exams = len(submissions)
	if total_exams == 0:
		return {"total_exams": 0, "average_score": "0%", "best_score": "0%"}

	percentages = [submission.percentage for submission in submissions if submission.percentage is not None]
	if not percentages:
		return {"total_exams": total_exams, "average_score": "0%", "best_score": "0%"}

	best_score = max(percentages)
	average_score = sum(percentages) / len(percentages)
	return {
		"total_exams": total_exams,
		"average_score": f"{round(average_score)}%",
		"best_score": f"{round(best_score)}%",
	}
