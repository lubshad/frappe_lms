import frappe
from frappe.model.document import Document


class CourseGroup(Document):
	def validate(self) -> None:
		self._validate_no_duplicate_courses()

	def _validate_no_duplicate_courses(self) -> None:
		seen: set[str] = set()
		for row in self.get("courses", []):
			if row.course in seen:
				frappe.throw(f"Course {row.course} is added more than once.")
			seen.add(row.course)
