import frappe
from lms.lms.doctype.lms_batch_enrollment.lms_batch_enrollment import LMSBatchEnrollment

class CustomLMSBatchEnrollment(LMSBatchEnrollment):
	def validate_duplicate_members(self) -> None:
		# Restrict to only one batch enrollment across all batches
		existing_enrollment = frappe.db.get_value(
			"LMS Batch Enrollment",
			{"member": self.member, "name": ["!=", self.name]},
			["batch", "batch.title as batch_title"],
			as_dict=True
		)
		
		if existing_enrollment:
			frappe.throw(
				f"User is already enrolled in another batch: {existing_enrollment.batch_title} ({existing_enrollment.batch})"
			)

	def validate_course_enrollment(self) -> None:
		courses = frappe.get_all("Batch Course", filters={"parent": self.batch}, fields=["course"])

		for course in courses:
			if not frappe.db.exists(
				"LMS Enrollment",
				{"course": course.course, "member": self.member},
			):
				enrollment = frappe.new_doc("LMS Enrollment")
				enrollment.course = course.course
				enrollment.member = self.member
				enrollment.member_type = self.member_type or "Student"
				enrollment.enrollment_from_batch = self.batch
				enrollment.save()
			else:
				# Update member_type if it already exists but might be different
				# Optional: user might want this to stay in sync
				frappe.db.set_value("LMS Enrollment", {"course": course.course, "member": self.member}, "member_type", self.member_type or "Student")
