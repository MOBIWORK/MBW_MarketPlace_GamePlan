# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import get_fullname
from gameplan.utils import extract_mentions
from frappe.core.doctype.communication.email import make
from gameplan.utils import get_config_notification_by_user

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
			userMention = frappe.get_doc('User', mention.email)
			user_sender = frappe.get_doc('User', self.owner)
			type_notifys = []
			config_notification = get_config_notification_by_user(userMention)
			if config_notification[5]["arr_permission"][0]["email"] == True:
				type_notifys.append("email")
			if config_notification[5]["arr_permission"][0]["browser"] == True:
				type_notifys.append('browser')
			if "email" in type_notifys:
				content_email = ""
				link_btn = ""
				if "GP Task" in [self.doctype, self.get('reference_doctype')]:
					task_info = frappe.get_doc("GP Task", self.reference_name)
					if task_info.project is not None and task_info.project != "":
						project_info = frappe.get_doc('GP Project', task_info.project)
						link_btn = frappe.utils.get_url(f'/g/{project_info.team}/projects/{project_info.name}/task/{task_info.name}')
						content_email = f"""
							<div class="mb-2 leading-5 text-gray-600">
								<div>
									Dự án {project_info.title} - {title} 
								</div
								<div>{get_fullname(self.owner)} đã nhắc đến bạn: </div>
								<div>
									{self.content}
								</div>
							</div>
							<p><a class="btn btn-primary" href="{link_btn}">Xem chi tiết</a></p>
						"""
					else:
						link_btn = frappe.utils.get_url(f'/g/task/{task_info.name}')
						content_email = f"""
							<div class="mb-2 leading-5 text-gray-600">
								<div>
									{title} 
								</div
								<div>{get_fullname(self.owner)} đã nhắc đến bạn: </div>
								<div>
									{self.content}
								</div>
							</div>
							<p><a class="btn btn-primary" href="{link_btn}">Xem chi tiết</a></p>
						"""
				elif "GP Discussion" in [self.doctype, self.get('reference_doctype')]:
					discussion_info = frappe.get_doc('GP Discussion', self.reference_name)
					project_info = frappe.get_doc('GP Project', discussion_info.project)
					link_btn = frappe.utils.get_url(f'/g/{project_info.team}/projects/{project_info.name}/discussion/{discussion_info.name}')
					content_email = f"""
						<div class="mb-2 leading-5 text-gray-600">
							<div>
								Dự án {project_info.title} - {title} 
							</div
							<div>{get_fullname(self.owner)} đã nhắc đến bạn: </div>
							<div>
								{self.content}
							</div>
						</div>
						<p><a class="btn btn-primary" href="{link_btn}">Xem chi tiết</a></p>
					"""
				make(
					doctype=self.doctype,
					name=self.reference_name,
					content = content_email,
					recipients = userMention.email,
					send_email = True,
					sender = user_sender.email,
					sender_full_name = user_sender.full_name,
					subject = f'[TEAM] {get_fullname(self.owner)} đã nhắc đến bạn'
				)
				frappe.db.commit()
