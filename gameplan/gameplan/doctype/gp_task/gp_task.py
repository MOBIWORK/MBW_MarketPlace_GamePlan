# Copyright (c) 2022, Frappe Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from gameplan.extends.client import check_permissions
from gameplan.gameplan.doctype.gp_notification.gp_notification import GPNotification
from gameplan.mixins.activity import HasActivity
from gameplan.mixins.mentions import HasMentions
from gameplan.search import GameplanSearch 
from gameplan.notification import assign_to_someone_task, change_status_owner_task, change_assignee_to_older, change_due_date_to_assignee, change_priority_to_assignee
from datetime import datetime, timedelta
import json

class GPTask(HasMentions, HasActivity, Document):
	on_delete_cascade = ["GP Comment", "GP Activity"]
	on_delete_set_null = ["GP Notification"]
	activities = ['Task Value Changed']
	mentions_field = 'description'

	def before_insert(self):
		if not self.status:
			self.status = 'Backlog'

	def after_insert(self):
		self.update_tasks_count(1)
		if frappe.session.user != self.assigned_to:
			assign_to_someone_task(self.project, self.name, frappe.session.user, self.assigned_to, self.title)
		self.insert_reminder()

	def on_update(self):
		self.update_project_progress()
		self.notify_mentions()
		self.log_value_updates()
		self.update_search_index()
	
	def before_save(self):
		task_exist = frappe.db.exists('GP Task', self.name)
		if task_exist is not None:
			task_info = frappe.db.get_value('GP Task', self.name, ['assigned_to', 'status', 'owner', 'due_date', 'priority'], as_dict=1)
			if task_info.assigned_to != self.assigned_to and self.assigned_to != frappe.session.user:
				assign_to_someone_task(self.project, self.name, frappe.session.user, self.assigned_to, self.title)
			if task_info.assigned_to is not None and task_info.assigned_to != "":
				if task_info.assigned_to != self.assigned_to and task_info.assigned_to != frappe.session.user:
					change_assignee_to_older(self.name, self.assigned_to)
			if task_info.status != self.status and frappe.session.user != task_info.owner:
				change_status_owner_task(self.name, frappe.session.user, self.status)
			if task_info.due_date is not None:
				if task_info.due_date != self.due_date and frappe.session.user != self.assigned_to:
					change_due_date_to_assignee(self.name, self.due_date)
				if task_info.due_date != self.due_date:
					self.update_reminder()
			if task_info.priority is not None:
				if task_info.priority != self.priority and frappe.session.user != self.assigned_to:
					change_priority_to_assignee(self.name, self.priority)

	def insert_reminder(self):
		if self.due_date is None or self.due_date == "":
			return
		for config_reminder_task in self.reminders_config:
			if config_reminder_task.remind_times is not None and config_reminder_task.remind_times != "" and config_reminder_task.remind_times != 0:
				reminder = frappe.new_doc("GP Reminder")
				reminder_at, unit = self.render_reminder_at(self.due_date, config_reminder_task.remind_times, config_reminder_task.remind_unit)
				reminder.description = f"Nhiệm vụ {self.title} sẽ đến hạn trong {config_reminder_task.remind_times} {unit} nữa"
				reminder.remind_at = reminder_at
				reminder.user = self.assigned_to
				reminder.reminder_doctype = "GP Task"
				reminder.reminder_docname = self.name
				reminder.notified = 0
				reminder.reminder_times = config_reminder_task.remind_times
				reminder.reminder_unit = unit
				reminder.insert()
				frappe.db.set_value('GP Config Reminder Task', config_reminder_task.name, 'id_reminder', reminder.name)
				frappe.db.commit()

	def update_reminder(self):
		if self.due_date is None or self.due_date == "":
			return
		for reminder_config in self.reminders_config:
			if reminder_config.remind_times is not None and reminder_config.remind_times != "" and reminder_config.remind_times != 0:
				if isinstance(self.due_date, str):
					date_due_date = datetime.strptime(self.due_date, '%Y-%m-%d %H:%M:%S')
				else:
					date_due_date = self.due_date
				is_exist_remind = False
				if reminder_config.id_reminder is not None and reminder_config.id_reminder != "":
					is_exist_remind = True
				if is_exist_remind == True and date_due_date > datetime.now():
					id_reminder = reminder_config.id_reminder
					doc_reminder = frappe.get_doc('GP Reminder', id_reminder)
					reminder_at, unit = self.render_reminder_at(self.due_date, reminder_config.remind_times, reminder_config.remind_unit)
					doc_reminder.description = f"Nhiệm vụ {self.title} sẽ đến hạn trong {reminder_config.remind_times} {unit} nữa"
					doc_reminder.remind_at = reminder_at
					doc_reminder.user = self.assigned_to
					doc_reminder.reminder_doctype = "GP Task"
					doc_reminder.reminder_docname = self.name
					doc_reminder.notified = 0
					doc_reminder.reminder_times = reminder_config.remind_times
					doc_reminder.reminder_unit = unit
					doc_reminder.save()
					frappe.db.commit()
				elif is_exist_remind == False and date_due_date > datetime.now():
					self.insert_reminder()
	
	def render_reminder_at(self, due_date, remind_times, remind_unit):
		reminder_at = datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')
		unit = "phút"
		if remind_unit == "minute":
			remind_times = int(remind_times)
			new_minute = reminder_at.minute - remind_times
			# Điều chỉnh nếu phút âm
			while new_minute < 0:
				reminder_at = reminder_at.replace(hour=reminder_at.hour - 1)
				new_minute += 60
			reminder_at = reminder_at.replace(minute=new_minute)
		elif remind_unit == "hour":
			unit = "giờ"
			remind_times = int(remind_times)
			new_hour = reminder_at.hour - remind_times
			# Điều chỉnh nếu giờ âm
			while new_hour < 0:
				reminder_at = reminder_at.replace(day=reminder_at.day - 1)
				new_hour += 24
			reminder_at = reminder_at.replace(hour=new_hour)
		elif remind_unit == "day":
			unit = "ngày"
			remind_times = int(remind_times)
			new_day = reminder_at.day - remind_times
			# Điều chỉnh nếu ngày âm
			while new_day < 1:
				previous_month = reminder_at.replace(day=1) - timedelta(days=1)
				reminder_at = reminder_at.replace(month=previous_month.month, day=previous_month.day)
				new_day += previous_month.day
			reminder_at = reminder_at.replace(day=new_day)
		return reminder_at, unit

	def log_value_updates(self):
		fields = ['title', 'description', 'status', 'priority', 'assigned_to', 'due_date', 'project']
		for field in fields:
			prev_doc = self.get_doc_before_save()
			if prev_doc and str(self.get(field)) != str(prev_doc.get(field)):
				self.log_activity('Task Value Changed', data={
					'field': field,
					'field_label': self.meta.get_label(field),
					'old_value': prev_doc.get(field),
					'new_value': self.get(field)
				})

	def update_search_index(self):
		if self.has_value_changed('title') or self.has_value_changed('description'):
			search = GameplanSearch()
			search.index_doc(self)

	def on_trash(self):
		self.update_tasks_count(-1)
		search = GameplanSearch()
		search.remove_doc(self)

	def update_tasks_count(self, delta=1):
		if not self.project:
			return
		current_tasks_count = frappe.db.get_value("GP Project", self.project, "tasks_count") or 0
		frappe.db.set_value("GP Project", self.project, "tasks_count", current_tasks_count + delta)

	def update_project_progress(self):
		if self.project and self.has_value_changed("is_completed"):
			frappe.get_doc("GP Project", self.project).update_progress()

	@frappe.whitelist()
	def track_visit(self):
		GPNotification.clear_notifications(task=self.name)

@frappe.whitelist()
def get_list(fields=None, filters: dict|None=None, order_by=None, start=0, limit=20, group_by=None, parent=None, debug=False, txt_search=None, is_my_task=None):
	doctype = 'GP Task'
	check_permissions(doctype, parent)
	assigned_or_owner = filters.pop('assigned_or_owner', None)
	title_pop = filters.pop('title', None)
	search_by_project_team = filters.pop('search_by_project_team', None)
	Task = frappe.qb.DocType(doctype)
	if search_by_project_team is not None and search_by_project_team == True:
		project_id = filters.pop('project', None)
		if title_pop is not None and title_pop != "":
			Team = frappe.qb.DocType('GP Team')
			Project = frappe.qb.DocType('GP Project')
			query = frappe.qb.from_(Task).inner_join(Team).on(Task.team == Team.name).inner_join(Project).on(Task.project == Project.name).select(Task.name,Task.title,Task.description,Task.start_date,Task.due_date,Task.status,Task.priority,Task.is_completed,Task.completed_at,Task.completed_by,Task.project,Task.team,Task.assigned_to,Task.comments_count,Task.owner,Task.creation,Project.title.as_("project_title"),Team.title.as_("team_title"))
			query = query.where(Task.project == project_id)
			if assigned_or_owner:
				query = query.where(
					(Task.assigned_to == assigned_or_owner) | (Task.owner == assigned_or_owner)
				)
			if title_pop is not None and title_pop != "":
				query = query.where(Task.title.like(f'%{title_pop}%') | Team.title.like(f'%{title_pop}%') | Project.title.like(f'%{title_pop}%'))
			return query.run(as_dict=True, debug=debug)
		else:
			query = frappe.qb.get_query(
				table=doctype,
				fields=fields,
				order_by=order_by,
				offset=start,
				limit=limit,
				group_by=group_by,
			)
			query = query.where(Task.project == project_id)
			if assigned_or_owner:
				query = query.where(
					(Task.assigned_to == assigned_or_owner) | (Task.owner == assigned_or_owner)
				)
			tasks = query.run(as_dict=True, debug=debug)
			if order_by is not None and ',' not in order_by:
				for task in tasks:
					if task.priority == "":
						task["code_priority"] = 0
					elif task.priority == "Low":
						task["code_priority"] = 1
					elif task.priority == "Medium":
						task["code_priority"] = 2
					elif task.priority == "High":
						task["code_priority"] = 3
					elif task.priority == "Urgent":
						task["code_priority"] = 4
				if 'priority' in order_by and 'asc' in order_by:
					tasks.sort(key=myFuncSortedPriority)
				if 'priority' in order_by and 'desc' in order_by:
					tasks.sort(key=myFuncSortedPriority, reverse=True)
			return tasks
	else:
		query = frappe.qb.get_query(
			table=doctype,
			fields=fields,
			order_by=order_by,
			offset=start,
			limit=limit,
			group_by=group_by,
		)
		if title_pop is not None and title_pop != "":
			query = query.where(Task.title.like(f'%{title_pop}%'))
		if assigned_or_owner:
			query = query.where(
				(Task.assigned_to == assigned_or_owner) | (Task.owner == assigned_or_owner)
			)
		tasks = query.run(as_dict=True, debug=debug)
		if order_by is not None and ',' not in order_by:
			for task in tasks:
				if task.priority == "":
					task["code_priority"] = 0
				elif task.priority == "Low":
					task["code_priority"] = 1
				elif task.priority == "Medium":
					task["code_priority"] = 2
				elif task.priority == "High":
					task["code_priority"] = 3
				elif task.priority == "Urgent":
					task["code_priority"] = 4
			if 'priority' in order_by and 'asc' in order_by:
				tasks.sort(key=myFuncSortedPriority)
			if 'priority' in order_by and 'desc' in order_by:
				tasks.sort(key=myFuncSortedPriority, reverse=True)
		return tasks

def myFuncSortedPriority(e):
	return e["code_priority"]