import frappe

def execute():
    # Only run if the doc_type exists and the new child table is created.
    if not frappe.db.has_table("tabExam Program"):
        return

    # Check if the old 'program' column exists in 'tabExam'
    if not frappe.db.has_column("Exam", "program"):
        return

    # Fetch exams that have a single program assigned but no child records yet
    exams = frappe.db.sql("""
        SELECT name, program
        FROM `tabExam`
        WHERE program IS NOT NULL AND program != ''
    """, as_dict=True)

    for exam in exams:
        # Check if it already has child records to avoid duplicates
        if not frappe.db.count("Exam Program", filters={"parent": exam.name}):
            frappe.get_doc({
                "doctype": "Exam Program",
                "parent": exam.name,
                "parenttype": "Exam",
                "parentfield": "programs",
                "program": exam.program
            }).insert(ignore_permissions=True)

    # Note: We won't drop the 'program' column yet, Frappe handles schema cleanup.
