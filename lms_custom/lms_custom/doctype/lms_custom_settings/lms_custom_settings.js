frappe.ui.form.on("LMS Custom Settings", {
	refresh: function(frm) {
		frm.add_custom_button(__("Create Aptitude Course Groups"), () => {
			frm.events.run_setup(frm, "create_aptitude");
		}, __("Setup Scripts"));

		frm.add_custom_button(__("Create Higher Secondary Course Groups"), () => {
			frm.events.run_setup(frm, "create_higher_secondary");
		}, __("Setup Scripts"));

		frm.add_custom_button(__("Chartered Accounts Course Groups"), () => {
			frm.events.run_setup(frm, "create_professional");
		}, __("Setup Scripts"));
	},

	run_setup: function(frm, script_name) {
		frappe.call({
			method: "lms_custom.api.setup.run_setup_script",
			args: {
				script_name: script_name
			},
			callback: function(r) {
				if (r.message) {
					frappe.msgprint(r.message);
				}
			}
		});
	}
});
