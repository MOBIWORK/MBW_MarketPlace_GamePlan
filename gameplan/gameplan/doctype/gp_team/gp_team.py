# Copyright (c) 2022, Frappe Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
import gameplan
from frappe.model.document import Document
from frappe.model.naming import append_number_if_name_exists
from gameplan.gemoji import get_random_gemoji
from gameplan.mixins.archivable import Archivable
from pypika.terms import ExistsCriterion
from gameplan.notification import send_guest_by_invite_guest,change_limit_project_team,change_name_project_team
from gameplan.utils import random_config_notification
import json


class GPTeam(Archivable, Document):
	on_delete_cascade = ["GP Project"]
	on_delete_set_null = ["GP Notification"]

	def as_dict(self, *args, **kwargs) -> dict:
		members = [m.user for m in self.members]
		if self.is_private and frappe.session.user not in members:
			frappe.throw("Not permitted", frappe.PermissionError)

		d = super().as_dict(*args, **kwargs)
		return d

	@staticmethod
	def get_list_query(query):
		Team = frappe.qb.DocType('GP Team')
		Member = frappe.qb.DocType('GP Member')
		member_exists = (
			frappe.qb.from_(Member)
				.select(Member.name)
				.where(Member.parenttype == 'GP Team')
				.where(Member.parent == Team.name)
				.where(Member.user == frappe.session.user)
		)
		query = query.where(
			(Team.is_private == 0) | ((Team.is_private == 1) & ExistsCriterion(member_exists))
		)
		is_guest = gameplan.is_guest()
		if is_guest:
			Team = frappe.qb.DocType('GP Team')
			GuestAccess = frappe.qb.DocType('GP Guest Access')
			team_list = GuestAccess.select(GuestAccess.team).where(GuestAccess.user == frappe.session.user)
			query = query.where(Team.name.isin(team_list))
		return query

	def before_insert(self):
		if not self.name:
			slug = frappe.scrub(self.title).replace("_", "-")
			self.name = append_number_if_name_exists("GP Team", slug)

		if not self.icon:
			self.icon = get_random_gemoji().emoji

		if not self.readme:
			self.readme = f"""
			<h3>Welcome to the {self.title} team page!</h3>
			<p>You can add a brief introduction about the team, important links, resources, and other important information here.</p>
		"""

		self.add_member(frappe.session.user)
	
	def before_save(self):
		team_exist = frappe.db.exists('GP Team', self.name)
		if team_exist is not None:
			team_old = frappe.get_doc('GP Team', self.name)
			if team_old.is_private != self.is_private:
				change_limit_project_team("team", self.name)
			if team_old.title != self.title:
				change_name_project_team("team", self.name, team_old.title, self.title)

	def add_member(self, email):
		if email not in [member.user for member in self.members]:
			self.append("members", {
				"email": email,
				"user": email,
				"role": "manager",
				"status": "Accepted"
			})

	@frappe.whitelist()
	def add_members(self, users):
		for user in users:
			self.add_member(user)
			config_notifications = frappe.db.get_all(
				"GP Config Notification",
				fields=["config_notification"],
				filters={"user": user}
			)
			config_notification = []
			type_notify = []
			if len(config_notifications) == 0:
				configs = random_config_notification()
				doc_config_notification = frappe.new_doc('GP Config Notification')
				doc_config_notification.config_notification = json.dumps(configs)
				doc_config_notification.user = user
				doc_config_notification.insert(ignore_permissions=True)
				frappe.db.commit()
				config_notification = configs
			else:
				config_notification = json.loads(config_notifications[0].config_notification)
			if config_notification[1]["arr_permission"][0]["email"] == True:
				type_notify.append("email")
			if config_notification[1]["arr_permission"][0]["browser"] == True:
				type_notify.append('browser')
			send_guest_by_invite_guest(type_notify, user, "team", self.name)
		self.save()

	@frappe.whitelist()
	def remove_member(self, user):
		for member in self.members:
			if member.user == user:
				self.remove(member)
				self.save()
				break
