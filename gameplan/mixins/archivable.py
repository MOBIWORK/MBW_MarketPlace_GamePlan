# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from gameplan.notification import change_archived_project_team

class Archivable:
	'''
	Mixin to add archive and unarchive methods to a DocType. `archived_at` (Datetime) and
	`archived_by` (Link to User) fields are required for this mixin to work.
	'''
	@frappe.whitelist()
	def archive(self):
		self.archived_at = frappe.utils.now()
		self.archived_by = frappe.session.user

		#Viết thông báo archived ở đây
		self.save()
		if self.doctype == "GP Project":
			change_archived_project_team("project", self.name, frappe.session.user)
		elif self.doctype == "GP Team":
			change_archived_project_team("team", self.name, frappe.session.user)

	@frappe.whitelist()
	def unarchive(self):
		self.archived_at = None
		self.archived_by = None
		self.save()