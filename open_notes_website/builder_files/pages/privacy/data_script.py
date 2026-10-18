# The "change your choice" button only means something when analytics are set up.
data.analytics_on = bool(
	frappe.db.get_single_value("Open Notes Website Settings", "ga_measurement_id")
	or frappe.db.get_single_value("Open Notes Website Settings", "clarity_project_id")
)
