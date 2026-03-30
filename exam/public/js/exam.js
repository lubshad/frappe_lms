(function () {
	const workspaceNames = new Set(["Exam Management", "Content Management"]);
	const doctypeNames = new Set([
		"LMS Program",
		"LMS Course",
		"Course Chapter",
		"Course Lesson",
		"LMS Batch",
		"LMS Enrollment",
		"LMS Question",
		"LMS Quiz",
		"LMS Quiz Submission",
		"User",
	]);

	const textReplacements = new Map([
		["LMS Quiz Submission", "Exam Submission"],
		["Quiz Submission", "Exam Submission"],
		["LMS Quiz", "Exam"],
		["Quizzes", "Exams"],
		["Quiz", "Exam"],
		["Submissions", "Exam Submissions"],
	]);

	const routeMatches = (route) => {
		if (!Array.isArray(route) || route.length === 0) {
			return false;
		}

		const [view, entity] = route;
		if (view === "workspace" && workspaceNames.has(entity)) {
			return true;
		}

		return typeof entity === "string" && doctypeNames.has(entity);
	};

	const syncExamWidth = () => {
		const enabled = routeMatches(frappe.get_route());
		document.body.classList.toggle("exam-full-width", enabled);
		document.body.classList.toggle("full-width", enabled);
	};

	const replaceText = (value) => textReplacements.get(value) || value;

	const syncExamLabels = () => {
		const route = frappe.get_route();
		if (!routeMatches(route)) {
			return;
		}

		const entity = route[1];
		const page = frappe.container?.page;
		if (page?.page?.title && typeof entity === "string") {
			page.page.set_title(__(replaceText(entity)));
		}

		const selectors = [
			".layout-main-section .title-text",
			".page-breadcrumbs .breadcrumb-item",
			".standard-sidebar-item .item-anchor",
			".desk-sidebar-item .item-anchor",
			".widget-head .widget-title",
			".shortcut-widget-box .widget-label",
			".number-card-title",
			".sidebar-item-label",
		];

		selectors.forEach((selector) => {
			document.querySelectorAll(selector).forEach((node) => {
				const text = node.textContent?.trim();
				if (!textReplacements.has(text)) {
					return;
				}
				node.textContent = replaceText(text);
			});
		});
	};

	frappe.ready(() => {
		syncExamWidth();
		syncExamLabels();
		frappe.router.on("change", () => {
			frappe.after_ajax(() => {
				syncExamWidth();
				syncExamLabels();
			});
		});
	});
})();
