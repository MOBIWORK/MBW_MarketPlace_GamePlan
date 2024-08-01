import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint
from frappe.utils.data import add_to_date, get_datetime, now_datetime
import json
from datetime import datetime
import math
from frappe.core.doctype.communication.email import make

class GPReminder(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		description: DF.SmallText
		notified: DF.Check
		remind_at: DF.Datetime
		reminder_docname: DF.DynamicLink | None
		reminder_doctype: DF.Link | None
		user: DF.Link
	# end: auto-generated types

	@staticmethod
	def clear_old_logs(days=30):
		from frappe.query_builder import Interval
		from frappe.query_builder.functions import Now
		table = frappe.qb.DocType("GP Reminder")
		frappe.db.delete(table, filters=(table.remind_at < (Now() - Interval(days=days))))

	def validate(self):
		self.user = frappe.session.user
		if get_datetime(self.remind_at) < now_datetime():
			frappe.throw(_("Reminder cannot be created in past."))

def send_reminders():
    # Ensure that we send all reminders that might be before next job execution.
	job_freq = cint(frappe.get_conf().scheduler_interval) or 240
	upper_threshold = add_to_date(now_datetime(), seconds=job_freq, as_string=True, as_datetime=True)
	lower_threshold = add_to_date(now_datetime(), hours=-1, as_string=True, as_datetime=True)

	pending_reminders = frappe.get_all(
		"GP Reminder",
		filters=[
			("remind_at", "<=", upper_threshold),
			("remind_at", ">=", lower_threshold),  # dont send too old reminders if failed to send
			("notified", "=", 0),
		],
		pluck="name",
	)
    
	doc_test = frappe.new_doc('Doc_Test')
	doc_test.label = "Dòng 56 " + str(pending_reminders) + str(upper_threshold) + str(lower_threshold)
	doc_test.save()
	for reminder_name in pending_reminders:
		send_notify_for_reminder(reminder_name)

def send_notify_for_reminder(name):
	if name is None:
		return
	frappe.db.set_value('GP Reminder', name, 'notified', 1)
	reminder_info = frappe.get_doc('GP Reminder', name)
	if reminder_info.reminder_doctype == "GP Task":
		doc_task = frappe.get_doc('GP Task', reminder_info.reminder_docname)
 		project_info = frappe.db.get_value('GP Project', doc_task.project, ['title', 'team'], as_dict=1)
		teamId = None
		if project_info is not None:
			teamId = project_info.team
		unit = "phút"
		if self.remind_unit == "hour":
			unit = "giờ"
		elif self.remind_unit == "day":
			unit = "ngày"
		notification_text_task = f"""
			<div class="mb-2 leading-5 text-gray-600">
				<span>Nhiệm vụ </span>
				<span class="font-medium text-gray-900"> {doc_task.title} </span>
				<span>sẽ đến hạn trong {doc_task.remind_times} {unit} nữa</span>
			</div>
		"""
		values_notify = frappe._dict(
			from_user=doc_task.owner,
			to_user=doc_task.assigned_to,
			message=notification_text_task,
			doctype="GP Notification",
			project=doc_task.project,
			team=teamId,
			task=doc_task.name,
			type="Task"
		)
		if frappe.db.exists("GP Notification", values_notify) is None:
			frappe.get_doc(values_notify).insert()
			frappe.db.commit()
		if doc_task.notify_email == 1:
			user_recipient = frappe.get_doc('User', doc_task.assigned_to)
			user_sender = frappe.get_doc('User', doc_task.owner)
			link_btn = ""
			content_email = ""
			if project_info is not None and values_notify.project is not None and values_notify.project != "":
				link_btn = frappe.utils.get_url(f'/g/{values_notify.team}/projects/{values_notify.project}/task/{doc_task.name}')
				content_email = f"""
 				<div class="mb-2 leading-5 text-gray-600">
 				<div>
 				<span>Dự án </span>
 				<span>{project_info.title}</span>
 				</div>
 				<div>Nhiệm vụ {task_info.title} sẽ đến hạn trong {doc_task.remind_times} {unit} nữa</div>
 				</div>
 				<p><a class="btn btn-primary" href="{link_btn}">Xem chi tiết</a></p>
 				"""
			else:
 				link_btn = frappe.utils.get_url(f'/g/task/{doc_task.name}')
 				content_email = f"""
 				<div class="mb-2 leading-5 text-gray-600">
 				<div>Nhiệm vụ {task_info.title} sẽ đến hạn trong {doc_task.remind_times} {unit} nữa</div>
 				</div>
 				<p><a class="btn btn-primary" href="{link_btn}">Xem chi tiết</a></p>
 				"""
 			make(
 				doctype="GP Task",
 				name=doc_task.name,
 				content = content_email,
 				recipients = user_recipient.email,
 				send_email = True,
 				sender = user_sender.email,
 				sender_full_name = user_sender.full_name,
 				subject = f'[TEAM] Nhiệm vụ {task_info.title} sắp đến hạn'
 			)
 			frappe.db.commit()