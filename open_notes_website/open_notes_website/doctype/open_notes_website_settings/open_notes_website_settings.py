# Copyright (c) 2026, Adam Dawoodjee and contributors
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.model.document import Document

# The IDs are written into a <script> on every page, so only their documented
# shapes are accepted: anything else is a typo, or worse.
GA_ID = re.compile(r"^G-[A-Z0-9]{4,20}$")
CLARITY_ID = re.compile(r"^[a-z0-9]{6,20}$")


class OpenNotesWebsiteSettings(Document):
	def validate(self):
		self.ga_measurement_id = (self.ga_measurement_id or "").strip().upper()
		self.clarity_project_id = (self.clarity_project_id or "").strip().lower()
		if self.ga_measurement_id and not GA_ID.match(self.ga_measurement_id):
			frappe.throw(_("Google Analytics Measurement ID should look like G-XXXXXXXXXX."))
		if self.clarity_project_id and not CLARITY_ID.match(self.clarity_project_id):
			frappe.throw(_("Clarity Project ID should be the short letters-and-digits ID, e.g. abcd1234ef."))
