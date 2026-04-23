# Copyright (c) 2026, CoreAxis Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.pdf import get_pdf


class ExamSubmission(Document):
	
	@frappe.whitelist()
	def get_report_html(self) -> str:
		if not self.report_content:
			frappe.throw("Report content is not yet generated for this submission.")
		return self.report_content

	@frappe.whitelist()
	def send_report_email(self) -> None:
		if not self.report_content:
			frappe.throw("Report content is not yet generated for this submission.")

		subject = f"Exam Report - {self.exam_title}"
		response_html = self.report_content
		
		# Generate PDF
		pdf_content = get_pdf(response_html)
		
		# Save File to Frappe
		file_name = f"{self.name}_Report.pdf"
		
		_file = frappe.get_doc({
			"doctype": "File",
			"file_name": file_name,
			"attached_to_doctype": "Exam Submission",
			"attached_to_name": self.name,
			"content": pdf_content,
			"is_private": 1
		})
		_file.save(ignore_permissions=True)
		
		# Send Email
		user = frappe.get_cached_doc("User", self.member)
		
		frappe.sendmail(
			recipients=[user.email],
			subject=subject,
			message=response_html,
			attachments=[{"fname": file_name, "fcontent": pdf_content}],
			reference_doctype="Exam Submission",
			reference_name=self.name
		)
		
		# Mark report as sent
		self.db_set("report_sent", 1, update_modified=False)
		self.db_set("report_sent_on", frappe.utils.now(), update_modified=False)
		
		frappe.msgprint(f"Report emailed to {user.email} and attached successfully.", alert=True)

