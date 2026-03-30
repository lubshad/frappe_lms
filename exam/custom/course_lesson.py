import json
import frappe
from lms.lms.doctype.course_lesson.course_lesson import CourseLesson

class CustomCourseLesson(CourseLesson):
    def save_lesson_details_in_quiz(self, content):
        if not content:
            return

        try:
            data = json.loads(content)
            if not isinstance(data, dict):
                return
        except (json.JSONDecodeError, TypeError):
            return

        # Use the parsed data instead of self.content as the original does
        for block in data.get("blocks", []):
            if block.get("type") == "quiz":
                quiz = block.get("data").get("quiz")
                if quiz and frappe.db.exists("LMS Quiz", quiz):
                    frappe.db.set_value(
                        "LMS Quiz",
                        quiz,
                        {
                            "course": self.course,
                            "lesson": self.name,
                        },
                    )
