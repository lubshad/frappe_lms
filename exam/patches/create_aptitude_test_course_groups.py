import frappe

APTITUDE_TEST_GROUPS = [
	{"title": "Quantitative Aptitude", "description": "Quantitative Aptitude and Numerical Ability"},
	{"title": "Logical Reasoning", "description": "Logical Reasoning and Deductive Logic"},
	{"title": "Verbal Ability", "description": "Verbal Ability and Reading Comprehension"},
	{"title": "General Knowledge", "description": "General Knowledge and Awareness"},
	{"title": "Current Affairs", "description": "Current Affairs"},
	{"title": "Data Interpretation", "description": "Data Interpretation and Analysis"},
	{"title": "General English", "description": "General English Language Skills"},
]


def execute() -> None:
	"""Create Course Group records for Aptitude Tests."""
	_create_course_groups()
	frappe.db.commit()


def _create_course_groups() -> None:
	if not frappe.db.table_exists("Course Group"):
		return
	for group in APTITUDE_TEST_GROUPS:
		if frappe.db.exists("Course Group", group["title"]):
			continue
		doc = frappe.new_doc("Course Group")
		doc.title = group["title"]
		doc.description = group["description"]
		doc.insert(ignore_permissions=True)
