import frappe

def execute():
    """ Unhide the section break in Course Lesson to show YouTube URL and Quiz ID fields. """
    frappe.reload_doc("lms", "doctype", "course_lesson")

    # Update through DB directly as well to ensure it reflects in the desk
    frappe.db.set_value("DocField", {"parent": "Course Lesson", "fieldname": "section_break_6"}, "hidden", 0)
    
    # We also need to clear cache to see changes
    frappe.clear_cache(doctype="Course Lesson")
