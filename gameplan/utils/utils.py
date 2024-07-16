# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
import inspect
import re
from functools import wraps
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import json


def validate_url(url):
	result = urlparse(url)
	if not result.scheme:
		url = "https://" + url
		result = urlparse(url)
	return url if (result.scheme and result.netloc) else False


def extract_mentions(html):
	if not html:
		return []
	soup = BeautifulSoup(html, 'html.parser')
	mentions = []
	for d in soup.find_all('span', attrs={'data-type': 'mention'}):
		mentions.append(frappe._dict(full_name=d.get('data-label'), email=d.get('data-id')))
	return mentions


def remove_empty_trailing_paragraphs(html):
	from bs4 import BeautifulSoup

	soup = BeautifulSoup(html, 'html.parser')
	# remove p, br tags that are at the end with no content
	all_tags = soup.find_all(True)
	all_tags.reverse()
	for tag in all_tags:
		if tag.name in ['br', 'p'] and not tag.contents:
			tag.extract()
		else:
			# break on first non-empty tag
			break
	return str(soup)


def validate_type(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		sig = inspect.signature(func)
		annotated_types = {k: v.annotation for k, v in sig.parameters.items() if v.annotation != inspect._empty}
		bound_args = sig.bind(*args, **kwargs)
		bound_args.apply_defaults()
		for arg_name, arg_value in bound_args.arguments.items():
			if arg_name in annotated_types:
				if arg_value is not None and not isinstance(arg_value, annotated_types[arg_name]):
					raise TypeError(f"{func.__name__}: Argument {arg_name} must be of type {annotated_types[arg_name]}")
		return func(*args, **kwargs)
	return wrapper

def url_safe_slug(text):
	if not text:
		return text
	slug = re.sub(r'[^A-Za-z0-9\s-]+', '', text.lower())
	slug = slug.replace('\n', ' ')
	slug = slug.split(' ')
	slug = [part for part in slug if part]
	slug = '-'.join(slug)
	slug = re.sub('[-]+', '-', slug)
	return slug

def random_config_notification():
	config_notifications = [
		{
			'id': "manage_guest",
			'arr_permission': [
				{
					'id': "guest_joining",
					'email': True,
					'browser': False
				}
			]
		},{
			'id': "team_project",
			'arr_permission': [
				{
					'id': "adding_team_project",
					'email': True,
					'browser': False
				},{
					'id': "changing_per_team_project",
					'email': True,
					'browser': False
				},{
					'id': "archiving_team_project",
					'email': True,
					'browser': False
				},{
					'id': "changing_name_team_project",
					'email': True,
					'browser': False
				}
			]
		},{
			'id': "project_content",
			'arr_permission': [
				{
					'id': "adding_discussion_project",
					'email': True,
					'browser': False
				},{
					'id': "adding_page_project",
					'email': True,
					'browser': False
				},{
					'id': "updating_description_project",
					'email': True,
					'browser': False
				}
			]
		},{
			'id': "discussion",
			'arr_permission': [
				{
					'id': "adding_comment_discussion",
					'email': False,
					'browser': True
				},{
					'id': "adding_reaction_discussion",
					'email': False,
					'browser': True
				},{
					'id': "adding_comment_discussion_follow",
					'email': False,
					'browser': True
				},{
					'id': "adding_poll_discussion_follow",
					'email': True,
					'browser': True
				},{
					'id': "closing_discussion_follow",
					'email': True,
					'browser': True
				}
			]
		},{
			'id': "task",
			'arr_permission': [
				{
					'id': "assign_task",
					'email': True,
					'browser': False
				},{
					'id': "changing_status_my_task",
					'email': True,
					'browser': False
				},{
					'id': "changing_assignee_task",
					'email': True,
					'browser': False
				},{
					'id': "changing_due_date_task",
					'email': True,
					'browser': False
				},{
					'id': "changing_priority_task",
					'email': True,
					'browser': False
				}
			]
		},{
			'id': "comment",
			'arr_permission': [
				{
					'id': "tagging_comment",
					'email': True,
					'browser': False
				},{
					'id': "repling_comment",
					'email': True,
					'browser': True
				},{
					'id': "reaction_comment",
					'email': False,
					'browser': True
				}
			]
		},{
			'id': "poll",
			'arr_permission': [
				{
					'id': "voting_poll",
					'email': True,
					'browser': False
				},{
					'id': "closing_poll",
					'email': True,
					'browser': True
				}
			]
		}
	]
	return config_notifications

def get_config_notification_by_user(user_info):
	config_notifications = frappe.db.get_all(
		"GP Config Notification",
		fields=["config_notification"],
		filters={"user": user_info.name}
	)
	config_notification = []
	if len(config_notifications) == 0:
		configs = random_config_notification()
		doc_config_notification = frappe.new_doc('GP Config Notification')
		doc_config_notification.config_notification = json.dumps(configs)
		doc_config_notification.user = user_info.name
		doc_config_notification.insert(ignore_permissions=True)
		frappe.db.commit()
		config_notification = configs
	else:
		config_notification = json.loads(config_notifications[0].config_notification)
	return config_notification

def get_title_by_id_notification(idNotifycation):
	if idNotifycation == "manage_guest":
		return "Manage guest"
	elif idNotifycation == "guest_joining":
		return "Khách được mời tham gia dự án"
	elif idNotifycation == "team_project":
		return "Team/Project"
	elif idNotifycation == "adding_team_project":
		return "Bạn được thêm vào nhóm hoặc dự án mới"
	elif idNotifycation == "changing_per_team_project":
		return "Nhóm/dự án thay đổi quyền riêng tư"
	elif idNotifycation == "archiving_team_project":
		return "Nhóm/dự án bị archived"
	elif idNotifycation == "changing_name_team_project":
		return "Đổi tên nhóm/dự án"
	elif idNotifycation == "project_content":
		return "Project content"
	elif idNotifycation == "adding_discussion_project":
		return "Có thảo luận mới"
	elif idNotifycation == "adding_page_project":
		return "Có page mới"
	elif idNotifycation == "updating_description_project":
		return "Cập nhật nội dung mô tả"
	elif idNotifycation == "discussion":
		return "Discussion"
	elif idNotifycation == "adding_comment_discussion":
		return "Thảo luận của bạn có bình luận mới"
	elif idNotifycation == "adding_reaction_discussion":
		return "Thảo luận của bạn có thả cảm xúc mới"
	elif idNotifycation == "adding_comment_discussion_follow":
		return "Thảo luận bạn đang theo dõi có bình luận mới"
	elif idNotifycation == "adding_poll_discussion_follow":
		return "Thảo luận bạn đang theo dõi có bình chọn mới"
	elif idNotifycation == "closing_discussion_follow":
		return "Thảo luận bạn đang theo dõi đóng và kết luận"
	elif idNotifycation == "task":
		return "Task"
	elif idNotifycation == "assign_task":
		return "Bạn được gán công việc mới"
	elif idNotifycation == "changing_status_my_task":
		return "Công việc do bạn tạo thay đổi trạng thái"
	elif idNotifycation == "changing_assignee_task":
		return "Công việc bạn được gán thay đổi người thực hiện"
	elif idNotifycation == "changing_due_date_task":
		return "Công việc bạn được gán thay đổi ngày hết hạn"
	elif idNotifycation == "changing_priority_task":
		return "Công việc bạn được gán thay đổi mức ưu tiên"
	elif idNotifycation == "comment":
		return "Comment"
	elif idNotifycation == "tagging_comment":
		return "Ai đó tag tên bạn trong một bình luận"
	elif idNotifycation == "repling_comment":
		return "Bình luận của bạn có người trả lời"
	elif idNotifycation == "reaction_comment":
		return "Bình luận của bạn có người thả cảm xúc"
	elif idNotifycation == "poll":
		return "Poll"
	elif idNotifycation == "voting_poll":
		return "Poll bạn tạo có người vote"
	elif idNotifycation == "closing_poll":
		return "Poll bạn tham gia đóng + kết quả"