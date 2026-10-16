# Copyright (c) 2026, Adam Dawoodjee and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase


# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]



class IntegrationTestOpenNotesWebsiteSettings(IntegrationTestCase):
	"""
	Integration tests for OpenNotesWebsiteSettings.
	Use this class for testing interactions between multiple components.
	"""

	def test_analytics_ids_are_normalised_and_checked(self):
		settings = frappe.get_single("Open Notes Website Settings")
		settings.ga_measurement_id = " g-abc123xyz "
		settings.clarity_project_id = "QXRP0B6JT0"
		settings.validate()
		self.assertEqual(settings.ga_measurement_id, "G-ABC123XYZ")
		self.assertEqual(settings.clarity_project_id, "qxrp0b6jt0")

		for field, bad in (
			("ga_measurement_id", "UA-12345-1"),
			("ga_measurement_id", "G-1');alert(1);//"),
			("clarity_project_id", "abc</script>"),
		):
			settings.reload()
			settings.set(field, bad)
			self.assertRaises(frappe.ValidationError, settings.validate)

	def test_empty_ids_are_allowed(self):
		settings = frappe.get_single("Open Notes Website Settings")
		settings.ga_measurement_id = ""
		settings.clarity_project_id = None
		settings.validate()
