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

HIGHER_SECONDARY_GROUPS = [
	{"title": "Mathematics", "description": "Higher Secondary Mathematics"},
	{"title": "Physics", "description": "Higher Secondary Physics"},
	{"title": "Chemistry", "description": "Higher Secondary Chemistry"},
	{"title": "Biology", "description": "Higher Secondary Biology"},
	{"title": "Computer Science", "description": "Higher Secondary Computer Science"},
	{"title": "English", "description": "Higher Secondary English"},
	{"title": "History", "description": "Higher Secondary History"},
	{"title": "Geography", "description": "Higher Secondary Geography"},
	{"title": "Economics", "description": "Higher Secondary Economics"},
	{"title": "Accountancy", "description": "Higher Secondary Accountancy"},
	{"title": "Business Studies", "description": "Higher Secondary Business Studies"},
	{"title": "Political Science", "description": "Higher Secondary Political Science"},
	{"title": "Psychology", "description": "Higher Secondary Psychology"},
	{"title": "Sociology", "description": "Higher Secondary Sociology"},
	{"title": "Physical Education", "description": "Higher Secondary Physical Education"},
]

PROFESSIONAL_COURSES = [
	{"title": "CA", "description": "Chartered Accountancy"},
	{"title": "ACCA", "description": "Association of Chartered Certified Accountants"},
	{"title": "CMA (INDIA)", "description": "Cost and Management Accountant (India)"},
	{"title": "CMA (USA)", "description": "Certified Management Accountant (USA)"},
	{"title": "CS", "description": "Company Secretary"},
]

@frappe.whitelist()
def run_setup_script(script_name: str) -> str:
	"""Run predefined setup scripts to populate Course Groups."""
	frappe.only_for("System Manager")

	if script_name == "create_aptitude":
		_create_groups(APTITUDE_TEST_GROUPS)
		return "Aptitude Course Groups created or updated successfully."
	elif script_name == "create_higher_secondary":
		_create_groups(HIGHER_SECONDARY_GROUPS)
		return "Higher Secondary Course Groups created or updated successfully."
	elif script_name == "create_professional":
		_create_groups(PROFESSIONAL_COURSES)
		return "Chartered Accounts Course Groups created or updated successfully."
	else:
		frappe.throw("Invalid setup script requested.")

def _create_groups(group_list: list[dict]) -> None:
	if not frappe.db.table_exists("Course Group"):
		frappe.throw("Course Group DocType not found. Please run migration first.")
	
	for group in group_list:
		if frappe.db.exists("Course Group", group["title"]):
			continue
		doc = frappe.new_doc("Course Group")
		doc.title = group["title"]
		doc.description = group["description"]
		doc.insert(ignore_permissions=True)
	
	frappe.db.commit()
