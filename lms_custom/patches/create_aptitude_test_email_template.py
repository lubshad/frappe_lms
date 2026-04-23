import frappe

def execute():
    # 1. Create Email Template
    template_name = "Aptitude Test Report"
    
    html_content = """
<!DOCTYPE html>
<html>
<head>
<style>
    body { font-family: 'Inter', -apple-system, sans-serif; background-color: #f8fafc; color: #1e293b; margin: 0; padding: 0; }
    .container { max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
    .header { background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); padding: 40px 20px; text-align: center; color: white; }
    .header h1 { margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.025em; }
    .content { padding: 40px 32px; }
    .greeting { font-size: 18px; font-weight: 600; margin-bottom: 12px; }
    .intro { color: #64748b; font-size: 15px; line-height: 1.6; margin-bottom: 32px; }
    .score-card { background: #f1f5f9; border-radius: 12px; padding: 32px 24px; text-align: center; margin-bottom: 32px; border: 1px solid #e2e8f0; }
    .score-label { font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700; margin-bottom: 8px; }
    .score-value { font-size: 56px; font-weight: 800; color: #4f46e5; margin: 0; line-height: 1; }
    .score-total { font-size: 18px; color: #94a3b8; font-weight: 600; margin-top: 4px; }
    .details { width: 100%; border-collapse: collapse; margin-bottom: 32px; }
    .details td { padding: 16px 0; border-bottom: 1px solid #f1f5f9; font-size: 14px; }
    .details td:first-child { color: #64748b; font-weight: 500; }
    .details td:last-child { text-align: right; font-weight: 600; color: #1e293b; }
    .footer { text-align: center; padding: 32px; font-size: 12px; color: #94a3b8; background: #f8fafc; border-top: 1px solid #f1f5f9; }
</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Aptitude Test Report</h1>
        </div>
        <div class="content">
            <p class="greeting">Hi {{ doc.member_name }},</p>
            <p class="intro">
                Great job! You've successfully completed the <strong>{{ doc.exam_title }}</strong>. 
                Our analysis shows a clear picture of your current aptitude profile.
            </p>
            
            <div class="score-card">
                <div class="score-label">Overall Performance</div>
                <div class="score-value">{{ doc.total_score }}</div>
                <div class="score-total">out of {{ doc.total_max_marks }}</div>
                <div style="margin-top: 16px; font-weight: 700; color: #4f46e5; font-size: 16px;">
                    {{ doc.percentage }}% Mastery
                </div>
            </div>

            <table class="details">
                <tr>
                    <td>Assessment ID</td>
                    <td>{{ doc.name }}</td>
                </tr>
                <tr>
                    <td>Date of Completion</td>
                    <td>{{ doc.creation[:10] }}</td>
                </tr>
                <tr>
                    <td>Result Status</td>
                    <td style="color: {{ '#059669' if doc.passed else '#dc2626' }}">
                        {{ 'SUCCESSFUL' if doc.passed else 'FURTHER PRACTICE NEEDED' }}
                    </td>
                </tr>
            </table>

            <p style="font-size: 14px; color: #64748b; text-align: center; margin-top: 32px;">
                A comprehensive analysis report has been attached to this email as a PDF. 
                Please review it to understand your strengths and areas for improvement.
            </p>
        </div>
        <div class="footer">
            &copy; 2026 CoreAxis Solutions. Empowering students through technology.
        </div>
    </div>
</body>
</html>
"""

    if not frappe.db.exists("Email Template", template_name):
        frappe.get_doc({
            "doctype": "Email Template",
            "name": template_name,
            "subject": "Aptitude Test Report: {{ doc.exam_title }}",
            "response": html_content,
            "use_html": 1
        }).insert()
    else:
        doc = frappe.get_doc("Email Template", template_name)
        doc.subject = "Aptitude Test Report: {{ doc.exam_title }}"
        doc.response = html_content
        doc.use_html = 1
        doc.save()

    # 2. Attach to Exam
    exams = frappe.get_all("Exam", filters={"title": ["like", "%Aptitude%"]})
    for exam in exams:
        frappe.db.set_value("Exam", exam.name, "report_email_template", template_name)
