# Copyright (c) 2023, Frappe Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from .gp_poll_attributes import GPPollAttributes
from gameplan.notification import add_poll_followed_discussion, vote_poll_by_someone, close_poll
from gameplan.utils import get_config_notification_by_user

class GPPoll(Document, GPPollAttributes):
	def before_insert(self):
		self.options = [d for d in self.options if d.title]
		for option in self.options:
			option.title = option.title.strip()
		# dont allow duplicate options
		options = [d.title for d in self.options]
		if len(set(options)) != len(options):
			frappe.throw(frappe._("Duplicate options not allowed"))

	def validate(self):
		self.total_votes = len(self.votes)

	def after_insert(self):
		discussion = frappe.get_doc("GP Discussion", self.discussion)
		discussion.last_post_at = frappe.utils.now()
		discussion.last_post_by = frappe.session.user
		discussion.comments_count = discussion.comments_count + 1
		discussion.update_participants_count()
		discussion.track_visit()
		discussion.save(ignore_permissions=True)
		#Gửi thông báo cho người dùng đã theo dõi project
		project_discussion = frappe.db.get_value('GP Discussion', self.discussion, 'project')
		arr_user_followed = frappe.db.get_list('GP Followed Project', {project: project_discussion})
		id_users_followed = [ item.user for item in arr_user_followed]
		add_poll_followed_discussion(id_users_followed, self.discussion, self.name)

	@frappe.whitelist()
	def submit_vote(self, option):
		self.check_if_stopped()
		if self.anonymous:
			self.submit_anonymous_vote(option)
		else:
			self.submit_non_anonymous_vote(option)
		vote_poll_by_someone(self.name, frappe.session.user, option)

	def submit_anonymous_vote(self, option):
		for d in self.votes:
			if d.user == frappe.session.user:
				return
		for _option in self.options:
			if _option.title == option:
				self.append("votes", {"user": frappe.session.user})
				_option.votes += 1
				break

		self.total_votes = len(self.votes)
		for _option in self.options:
			_option.percentage = flt(_option.votes * 100 / self.total_votes, 2)
		self.save()

	def submit_non_anonymous_vote(self, option):
		for d in self.votes:
			if d.user == frappe.session.user:
				return

		self.append("votes", {"user": frappe.session.user, "option": option})
		self.total_votes = len(self.votes)
		for _option in self.options:
			_option.votes = len([d for d in self.votes if d.option == _option.title])
			_option.percentage = flt(_option.votes * 100 / self.total_votes, 2)
		self.save()

	@frappe.whitelist()
	def retract_vote(self):
		self.check_if_stopped()
		if self.anonymous:
			frappe.throw(frappe._("Cannot retract vote for anonymous poll"))
		self.votes = [d for d in self.votes if d.user != frappe.session.user]
		self.total_votes = len(self.votes)
		for _option in self.options:
			_option.votes = len([d for d in self.votes if d.option == _option.title])
			_option.percentage = flt(_option.votes * 100 / self.total_votes, 2) if self.total_votes else 0
		self.save()

	@frappe.whitelist()
	def stop_poll(self):
		if frappe.session.user != self.owner:
			frappe.throw(frappe._("Only owner can stop the poll"))
		self.stopped_at = frappe.utils.now()
		self.save()
		close_poll(self.name)

	def check_if_stopped(self):
		if self.stopped_at and self.stopped_at < frappe.utils.now_datetime():
			frappe.throw(frappe._("Poll has ended"))


@frappe.whitelist()
def get_list(fields, filters=None, start=0, limit=20, order_by=None):
	query = frappe.qb.get_query('GP Poll',
		fields=fields,
		filters=filters,
		start=start,
		limit=limit,
		order_by=order_by
	)

	data = query.run(as_dict=1)
	return data