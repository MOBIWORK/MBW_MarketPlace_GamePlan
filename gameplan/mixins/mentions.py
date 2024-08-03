# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import get_fullname
from gameplan.utils import extract_mentions

class HasMentions:
	def notify_mentions(self):
		mentions_field = getattr(self, 'mentions_field', None)
		if not mentions_field:
			return

		mentions = extract_mentions(self.get(mentions_field))
		for mention in mentions:
			values = frappe._dict(
				from_user=self.owner,
				to_user=mention.email,
			)
			title = ""
			if self.doctype == "GP Discussion":
				values.discussion = self.name
				discussion_info = frappe.get_doc('GP Discussion', self.name)
				title = discussion_info.title
			if self.doctype == "GP Task":
				values.task = self.name
				values.project = self.project
				task_info = frappe.get_doc('GP Task', self.name)
				title = task_info.title
			elif self.doctype == "GP Comment":
				values.comment = self.name
				if self.reference_doctype == "GP Discussion":
					values.discussion = self.reference_name
				elif self.reference_doctype == "GP Task":
					values.task = self.reference_name
					values.project = frappe.db.get_value("GP Task", self.reference_name, "project")

			if frappe.db.exists("GP Notification", values):
				continue
			notification = frappe.get_doc(doctype='GP Notification')
			if "GP Task" in [self.doctype, self.get('reference_doctype')]:
				notification.message = f"""
					<div class="text-gray-700 text-sm">
						<span class="font-medium text-gray-900">{ get_fullname(self.owner) }</span>
						<span> đề cập bạn trong một công việc</span>
						<span class="font-medium text-gray-900"> {title}</span>
					</div>
				"""
			elif "GP Discussion" in [self.doctype, self.get('reference_doctype')]:
				notification.message = f"""
					<div class="text-gray-700 text-sm">
						<span class="text-sm font-medium text-gray-900">{ get_fullname(self.owner) }</span>
						<span> đề cập bạn trong một thảo luận</span>
						<span class="text-sm font-medium text-gray-900"> {title}</span>
					</div>
				"""
			notification.update(values)
			notification.insert(ignore_permissions=True)
