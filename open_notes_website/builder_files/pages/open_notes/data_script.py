# Links that appear only once their URL is set in Open Notes Website Settings.
data.web_url = frappe.db.get_single_value("Open Notes Website Settings", "web_app_url") or ""
data.android_url = frappe.db.get_single_value("Open Notes Website Settings", "android_download_url") or ""
# Visibility conditions only test truthiness, so "not set yet" needs its own key.
data.web_pending = not data.web_url
data.android_pending = not data.android_url
