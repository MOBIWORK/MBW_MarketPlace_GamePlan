# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

from __future__ import unicode_literals
import gameplan
import frappe
from frappe.utils import validate_email_address, split_emails, cstr
from gameplan.utils import validate_type, random_config_notification, get_title_by_id_notification
from frappe.translate import get_all_translations
from gameplan.notification import send_manager_by_invite_guest, send_guest_by_invite_guest
from frappe.model.document import get_controller
from frappe.utils import make_filter_tuple
from frappe.model import no_value_fields
from frappe import _
import json
from gameplan.fcm_manager import send_notification_to_user

@frappe.whitelist(allow_guest=True)
def get_user_info(user=None):
	if frappe.session.user == "Guest":
		frappe.throw("Authentication failed", exc=frappe.AuthenticationError)

	filters = {"roles.role": ["like", "Gameplan %"]}
	if user:
		filters["name"] = user

	users = frappe.qb.get_query(
		"User",
		filters=filters,
		fields=["name", "email", "enabled", "user_image", "full_name", "user_type"],
		order_by="full_name asc",
		distinct=True,
	).run(as_dict=1)

	roles = frappe.db.get_all("Has Role", filters={"parenttype": "User"}, fields=["role", "parent"])
	user_profiles = frappe.db.get_all(
		"GP User Profile",
		fields=["user", "name", "image", "image_background_color", "is_image_background_removed"],
		filters={"user": ["in", [u.name for u in users]]},
	)
	user_profile_map = {u.user: u for u in user_profiles}
	for user in users:
		if frappe.session.user == user.name:
			user.session_user = True
		user_profile = user_profile_map.get(user.name)
		if user_profile:
			user.user_profile = user_profile.name
			user.user_image = user_profile.image
			user.image_background_color = user_profile.image_background_color
			user.is_image_background_removed = user_profile.is_image_background_removed
		user_roles = [r.role for r in roles if r.parent == user.name]
		user.role = None
		for role in ["Gameplan Guest", "Gameplan Member", "Gameplan Admin"]:
			if role in user_roles:
				user.role = role
	return users

@frappe.whitelist()
def get_config_notifications():
	config_notifications = frappe.db.get_all(
		"GP Config Notification",
		fields=["config_notification"],
		filters={"user": frappe.session.user}
	)
	config_notification = []
	if len(config_notifications) == 0:
		configs = random_config_notification()
		doc_config_notification = frappe.new_doc('GP Config Notification')
		doc_config_notification.config_notification = json.dumps(configs)
		doc_config_notification.user = frappe.session.user
		doc_config_notification.insert(ignore_permissions=True)
		frappe.db.commit()
		config_notification = configs
	else:
		config_notification = json.loads(config_notifications[0].config_notification)
	for config in config_notification:
		config['title'] = get_title_by_id_notification(config['id'])
		for permission in config['arr_permission']:
			permission['title'] = get_title_by_id_notification(permission['id'])
	return config_notification

@frappe.whitelist()
def change_config_notification(id_config, type_notify, value_notify):
	try:
		config_notifications = frappe.db.get_all(
			"GP Config Notification",
			fields=["config_notification", "name"],
			filters={"user": frappe.session.user}
		)
		if len(config_notifications) > 0:
			config_notification = json.loads(config_notifications[0].config_notification)
			for config in config_notification:
				for permission in config['arr_permission']:
					if permission['id'] == id_config:
						value_parse = False
						if value_notify == "true":
							value_parse = True
						if type_notify == "email":
							permission['email'] = value_parse
						elif type_notify == "browser":
							permission['browser'] = value_parse
			frappe.db.set_value('GP Config Notification', config_notifications[0].name, 'config_notification', json.dumps(config_notification))
			frappe.db.commit()
		return "ok"
	except Exception as e:
		return "error"

@frappe.whitelist()
@validate_type
def change_user_role(user: str, role: str):
	if gameplan.is_guest():
		frappe.throw("Only Admin can change user roles")

	if role not in ["Gameplan Guest", "Gameplan Member", "Gameplan Admin"]:
		return get_user_info(user)[0]

	user_doc = frappe.get_doc("User", user)
	for _role in user_doc.roles:
		if _role.role in ["Gameplan Guest", "Gameplan Member", "Gameplan Admin"]:
			user_doc.remove(_role)
	user_doc.append_roles(role)
	user_doc.save(ignore_permissions=True)

	return get_user_info(user)[0]


@frappe.whitelist()
@validate_type
def remove_user(user: str):
	user_doc = frappe.get_doc("User", user)
	for _role in user_doc.roles:
		if _role.role in ["Gameplan Guest", "Gameplan Member", "Gameplan Admin"]:
			user_doc.remove(_role)
	#user_doc.enabled = 0
	user_doc.save(ignore_permissions=True)
	return user


@frappe.whitelist()
@validate_type
def invite_by_email(emails: str, role: str, projects: list = None):
	if not emails:
		return
	email_string = validate_email_address(emails, throw=False)
	email_list = split_emails(email_string)
	if not email_list:
		return
	existing_members = frappe.db.get_all("User", filters={"email": ["in", email_list]}, pluck="email")
	existing_invites = frappe.db.get_all(
		"GP Invitation",
		filters={"email": ["in", email_list], "role": ["in", ["Gameplan Admin", "Gameplan Member"]]},
		pluck="email",
	)
	if role == "Gameplan Guest":
		to_invite = list(set(email_list) - set(existing_invites))
	else:
		to_invite = list(set(email_list) - set(existing_members) - set(existing_invites))

	if projects:
		projects = frappe.as_json(projects, indent=None)
	for email in to_invite:
		frappe.get_doc(doctype="GP Invitation", email=email, role=role, projects=projects).insert(ignore_permissions=True)

@frappe.whitelist()
def unread_notifications():
	res = frappe.db.get_all("GP Notification", "count(name) as count", {"to_user": frappe.session.user, "read": 0})
	return res[0].count

@frappe.whitelist()
def all_notifications():
	res = frappe.db.get_all("GP Notification", "count(name) as count", {"to_user": frappe.session.user})
	return res[0].count

@frappe.whitelist()
def get_notifications_by_filter(status):
	filter_noiti = {"to_user": frappe.session.user}
	if status == "unread":
		filter_noiti["read"] = 0
	notifications = frappe.db.get_list('GP Notification', 
		filters = filter_noiti, 
		fields=['type', 'message', 'comment','discussion','task','project','team','read',"from_user","creation","name","is_assign_task", "page"],
		order_by='creation desc'
	)
	for notification in notifications:
		if notification["project"] is not None and notification["project"] != "":
			title = frappe.db.get_value('GP Project', notification["project"], 'title')
			notification["project_title"] = title
	return notifications

@frappe.whitelist()
def get_members_by_type(team_project, type_filter):
	arr_member = []
	if type_filter == "team":
		team_info = frappe.get_doc('GP Team', team_project)
		members = team_info.members
		for member in members:
			user_info = frappe.get_doc('User', member.user)
			member_info = {
				'email': user_info.email,
				'full_name': user_info.full_name,
				'id_user': user_info.name,
				'id': member.name
			}
			if member.role is not None and member.role != "":
				member_info["role"] = member.role
			else:
				member_info["role"] = "manager"
			arr_member.append(member_info)
	elif type_filter == "project":
		project_info = frappe.get_doc('GP Project', team_project)
		members = team_info.members
		for member in members:
			user_info = frappe.get_doc('User', member.user)
			member_info = {
				'email': user_info.email,
				'full_name': user_info.full_name,
				'id_user': user_info.name,
				'id': member.name
			}
			if member.role is not None and member.role != "":
				member_info["role"] = member.role
			else:
				member_info["role"] = "manager"
			arr_member.append(member_info)
	return arr_member

@frappe.whitelist()
def delete_member_by_id(id_member):
	frappe.delete_doc('GP Member', id_member)
	frappe.db.commit()
	return "ok"

@frappe.whitelist()
def update_role_member_by_id(id_member, role_member):
	doc_member = frappe.get_doc('GP Member', id_member)
	doc_member.role = role_member
	doc_member.save(ignore_permissions=True)
	frappe.db.commit()
	return "ok"

@frappe.whitelist(methods=["POST"])
def add_role_member_by_id(team_project, type_filter, id_user):
	member_res = {}
	reference_doc = None
	if type_filter == "team":
		reference_doc = "GP Team"
	else:
		reference_doc = "GP Project"
	if reference_doc is not None:
		doc_info = frappe.get_doc(reference_doc, team_project)
		if id_user not in [member.user for member in doc_info.members]:
			member_doc = frappe.new_doc('GP Member')
			member_doc.update({
				'parent': doc_info.name,
				'parentfield': 'members',
				'parenttype': reference_doc,
				'user': id_user,
				'role': 'member',
				"status": "Accepted"
			})
			member_doc.insert()
			frappe.db.commit()
			config_notifications = frappe.db.get_all(
				"GP Config Notification",
				fields=["config_notification"],
				filters={"user": id_user}
			)
			config_notification = []
			type_notify = []
			if len(config_notifications) == 0:
				configs = random_config_notification()
				doc_config_notification = frappe.new_doc('GP Config Notification')
				doc_config_notification.config_notification = json.dumps(configs)
				doc_config_notification.user = id_user
				doc_config_notification.insert(ignore_permissions=True)
				frappe.db.commit()
				config_notification = configs
			else:
				config_notification = json.loads(config_notifications[0].config_notification)
			if config_notification[1]["arr_permission"][0]["email"] == True:
				type_notify.append("email")
			if config_notification[1]["arr_permission"][0]["browser"] == True:
				type_notify.append('browser')
			send_guest_by_invite_guest(type_notify, id_user, "team", doc_info.name)
			user_info = frappe.get_doc('User', id_user)
			member_res["email"] = user_info.email
			member_res["full_name"] = user_info.full_name
			member_res["id_user"] = user_info.name
			member_res["id"] = member_doc.name
			member_res["role"] = member_doc.role
			return member_res
	return member_res

@frappe.whitelist()
def get_user_system_by_filter(txtSearch=None):
	or_filters = []
	if txtSearch is not None and txtSearch != "":
		or_filters = [
			["email","LIKE", f'%{txtSearch}%'],
			["full_name", "LIKE", f'%{txtSearch}%']
		]
	users = frappe.get_list('User',
		fields=['name','full_name','email'],
		or_filters=or_filters
	)
	return users

@frappe.whitelist(methods=["POST"])
def create_team(title, is_private, arr_member):
	try:
		team_doc = frappe.new_doc('GP Team')
		team_doc.title = title,
		team_doc.is_private = is_private
		print("Dòng 314 ", team_doc.name)
		team_doc.insert()
		print("Dòng 315 ", team_doc.name)
		frappe.db.commit()
		for member in arr_member:
			if member['id'] is not None and member['id'] != "":
				add_role_member_by_id(team_doc.name, "team", member['id'])
			else:
				first_name = member['email'].split("@")[0].title()
				user = frappe.get_doc(
					doctype="User",
					user_type="Website User",
					email=member['email'],
					send_welcome_email=0,
					first_name=first_name,
				).insert(ignore_permissions=True)
				user.append_roles("Gameplan Member")
				user.save(ignore_permissions=True)
				frappe.db.commit()
				add_role_member_by_id(team_doc.name, "team", user.name)
		return {'status': "ok", 'message': team_doc}
	except Exception as e:
		return {'status': "error", 'message': str(e)}

@frappe.whitelist()
def get_teams_by_role():
	user_doc = frappe.get_doc("User", frappe.session.user)
	arr_role = [_role.role for _role in user_doc.roles]
	teams = frappe.get_all('GP Team',
		fields=['name','title','icon','modified','creation','archived_at','is_private'],
		order_by='title asc',
		page_length=999
	)
	arr_team_res = []
	if "Gameplan Admin" in arr_role:
		arr_team_res = teams
	if "Gameplan Member" in arr_role:
		for team in teams:
			filters = {'parent': team.name}
			members = frappe.db.sql("""
				SELECT
					user
				FROM `tabGP Member`
				WHERE parent = %(parent)s
			""", values=filters, as_dict=1)
			if frappe.session.user in [member.user for member in members]:
				team_filter = [team_fil.name for team_fil in arr_team_res if team_fil.name == team.name]
				if len(team_filter) == 0:
					arr_team_res.append(team)
			else:
				if team.is_private == 0:
					team_filter = [team_fil.name for team_fil in arr_team_res if team_fil.name == team.name]
					if len(team_filter) == 0:
						arr_team_res.append(team)
	if "Gameplan Guest" in arr_role:
		teams_guest = frappe.get_all('GP Guest Access', 
			filters = {
				'user': frappe.session.user
			},
			fields=['name', 'team']
		)
		for team_guest in teams_guest:
			team_filter = [team_fil.name for team_fil in arr_team_res if team_fil.name == team_guest.team]
			if len(team_filter) == 0:
				team_source = [team_fil for team_fil in teams if team_fil.name == team_guest.team]
				arr_team_res.append(team_source[0])
	return arr_team_res

@frappe.whitelist()
def get_projects_by_role():
	user_doc = frappe.get_doc('User', frappe.session.user)
	arr_role = [_role.role for _role in user_doc.roles]
	projects = frappe.get_all('GP Project',
		fields=['name','title','icon','team','archived_at','is_private','modified','tasks_count','discussions_count','guests'],
		order_by='title asc',
		page_length=999
	)
	teams = frappe.get_all('GP Team',
		fields=['name','title','is_private']
	)
	arr_project_res = []
	if "Gameplan Admin" in arr_role:
		arr_project_res = projects
	if "Gameplan Member" in arr_role:
		for team in teams:
			projects_by_team = frappe.get_all('GP Project',
				fields=['name','title','icon','team','archived_at','is_private','modified','tasks_count','discussions_count','guests'],
				filters = {
					'team': team.name
				},
				order_by='title asc',
				page_length=999
			)
			filters = {'parent': team.name}
			members = frappe.db.sql("""
				SELECT
					user
				FROM `tabGP Member`
				WHERE parent = %(parent)s
			""", values=filters, as_dict=1)
			if frappe.session.user in [member.user for member in members]:
				for project in projects_by_team:
					project_filter = [project_fil.name for project_fil in arr_project_res if project_fil.name == project.name]
					if len(project_filter) == 0:
						arr_project_res.append(project)
			else:
				if team.is_private == 0:
					for project in projects_by_team:
						if project.is_private == 0:
							project_filter = [project_fil.name for project_fil in arr_project_res if project_fil.name == project.name]
							if len(project_filter) == 0:
								arr_project_res.append(project)
	if "Gameplan Guest" in arr_role:
		for project in projects:
			if project.is_private == 1:
				guest_access = frappe.get_all('GP Guest Access',
					filters={
						'project': project.name,
						'user': frappe.session.user
					}
				)
				if len(guest_access) > 0:
					project_filter = [project_fil.name for project_fil in arr_project_res if project_fil.name == project.name]
					if len(project_filter) == 0:
						arr_project_res.append(project)
	return arr_project_res

@frappe.whitelist(methods=["POST"])
def invite_member(email, teamId):
	try:
		if not email:
			return
		email_string = validate_email_address(email, throw=False)
		email_list = split_emails(email_string)
		if not email_list:
			return
		existing_members = frappe.db.get_all("User", filters={"email": ["in", email_list]}, pluck="email")
		user_name = ""
		if len(existing_members) == 0:
			first_name = email.split("@")[0].title()
			user = frappe.get_doc(
				doctype="User",
				user_type="Website User",
				email=email,
				send_welcome_email=0,
				first_name=first_name,
			).insert(ignore_permissions=True)
			user.append_roles("Gameplan Member")
			user.save(ignore_permissions=True)
			frappe.db.commit()
			user_name = user.name
		else:
			user = frappe.get_doc({
				'doctype': 'User',
				'email': 'email'
			})
			user_name = user.name
		member_info = add_role_member_by_id(teamId, "team", user_name)
		return {'status': "ok", 'message': member_info}
	except Exception as e:
		return {'status': "error", 'message': ""}
	
@frappe.whitelist()
def get_connections(reference_doctype, reference_name):
	connections_res = []
	connections_filter = frappe.db.get_list('GP Connection',
		filters={
			'reference_type_source': reference_doctype,
			'reference_name_source': reference_name
		},
		fields=['name', 'reference_type_source', 'reference_name_source', 'reference_type_destination', 'reference_name_destination']
	)
	for connection_filter in connections_filter:
		connection_res_filter = [connecton_fil['name'] for connecton_fil in connections_res if connecton_fil['name'] == connection_filter['name']]
		if len(connection_res_filter) == 0:
			destination_info = frappe.get_doc(connection_filter.reference_type_destination, connection_filter.reference_name_destination)
			connection_res = {
				'name': connection_filter.name,
				'doctype_destination': connection_filter.reference_type_destination,
				'name_destination': connection_filter.reference_name_destination,
				'title_destination': destination_info.title,
				'team_destination': destination_info.team,
				'project_destination': destination_info.project
			}
			connections_res.append(connection_res)
	connections_filter = frappe.db.get_list('GP Connection',
		filters={
			'reference_type_destination': reference_doctype,
			'reference_name_destination': reference_name
		},
		fields=['name', 'reference_type_source', 'reference_name_source', 'reference_type_destination', 'reference_name_destination']
	)
	for connection_filter in connections_filter:
		connection_res_filter = [connecton_fil['name'] for connecton_fil in connections_res if connecton_fil['name'] == connection_filter['name']]
		if len(connection_res_filter) == 0:
			destination_info = frappe.get_doc(connection_filter.reference_type_source, connection_filter.reference_name_source)
			connection_res = {
				'name': connection_filter.name,
				'doctype_destination': connection_filter.reference_type_source,
				'name_destination': connection_filter.reference_name_source,
				'title_destination': destination_info.title,
				'team_destination': destination_info.team,
				'project_destination': destination_info.project
			}
			connections_res.append(connection_res)
	return connections_res

@frappe.whitelist()
def delete_connections(reference_doctype, reference_name):
	try:
		frappe.db.delete('GP Connection', {
			'reference_type_source': reference_doctype,
			'reference_name_source': reference_name
		})
		frappe.db.delete('GP Connection', {
			'reference_type_destination': reference_doctype,
			'reference_name_destination': reference_name
		})
		frappe.db.commit()
		return "ok"
	except Exception as e:
		return "error"


def convert_filter_to_tuple(doctype, filters):
	if isinstance(filters, dict):
		filters_items = filters.items()
		filters = []
		for key, value in filters_items:
			filters.append(make_filter_tuple(doctype, key, value))
	return filters

@frappe.whitelist()
def get_data_kanban(
	doctype: str,
	filters: str,
	text_search: str,
	is_my_task: str,
	order_by: str,
	page_length=20,
	page_length_count=20,
	column_field=None,
	title_field=None,
	columns=[],
	rows=[],
	kanban_columns=[],
	kanban_fields=[],
	default_filters=None,
	project=None,
	assign_task=[]
):
	filters = frappe.parse_json(filters)
	rows = frappe.parse_json(rows or "[]")
	columns = frappe.parse_json(columns or "[]")
	kanban_fields = frappe.parse_json(kanban_fields or "[]")
	kanban_columns = frappe.parse_json(kanban_columns or "[]")
	for key in filters:
		value = filters[key]
		if isinstance(value, list):
			if "@me" in value:
				value[value.index("@me")] = frappe.session.user
			elif "%@me%" in value:
				index = [i for i, v in enumerate(value) if v == "%@me%"]
				for i in index:
					value[i] = "%" + frappe.session.user + "%"
		elif value == "@me":
			filters[key] = frappe.session.user

	if default_filters:
		default_filters = frappe.parse_json(default_filters)
		filters.update(default_filters)

	is_default = True
	data = []
	_list = get_controller(doctype)
	if hasattr(_list, "default_list_data"):
		rows = _list.default_list_data().get("rows")
	if kanban_columns and column_field:
		field_meta = frappe.get_meta(doctype).get_field(column_field)
		if field_meta.fieldtype == "Link":
			kanban_columns = frappe.get_all(
				field_meta.options,
				fields=["name"],
				order_by="modified asc",
			)
		elif field_meta.fieldtype == "Select":
			kanban_columns = [{"name": option} for option in field_meta.options.split("\n") if option != ""]
		if not title_field:
			title_field = "name"
			if hasattr(_list, "default_kanban_settings"):
				title_field = _list.default_kanban_settings().get("title_field")
		if title_field not in rows:
			rows.append(title_field)
		if not kanban_fields:
			kanban_fields = ["name"]
			if hasattr(_list, "default_kanban_settings"):
				kanban_fields = json.loads(_list.default_kanban_settings().get("kanban_fields"))
		for field in kanban_fields:
			if field not in rows:
				rows.append(field)
		for kc in kanban_columns:
			column_filters = { column_field: kc.get('name') }
			order = kc.get("order")
			if column_field in filters and filters.get(column_field) != kc.name or kc.get('delete'):
				column_data = []
			else:
				column_filters.update(filters.copy())
				page_length = 20
				or_filters = []
				if kc.get("page_length"):
					page_length = kc.get("page_length")
				if order:
					column_data = get_records_based_on_order(doctype, rows, column_filters, page_length, order)
				else:
					if text_search is not None and text_search != "":
						if is_my_task == "true":
							projects = frappe.get_list('GP Project', filters={'title': ['like', f'%{text_search}%']},fields=['name', 'title'])
							teams = frappe.get_list('GP Team', filters={'title': ['like', f'%{text_search}%']}, fields=['name', 'title'])
							for project in projects:
								or_filters.append(['project', '=', project.name])
							for team in teams:
								or_filters.append(['team', '=', team.name])
							or_filters.append(['title', 'like', f'%{text_search}%'])
						else:
							or_filters.append(['title', 'like', f'%{text_search}%'])
						filter_column_data = convert_filter_to_tuple(doctype, column_filters)
						if project is not None and project != "":
							filter_column_data.append(['GP Task', 'project', '=', project])
						if assign_task is not None and len(assign_task) > 0:
							filter_column_data.append(['GP Task', 'assigned_to', 'in', assign_task])
						column_data = frappe.get_list(
							doctype,
							fields=rows,
							filters= filter_column_data,
							order_by=order_by,
							page_length=page_length,
							or_filters=or_filters
						)
						if is_my_task == "true":
							column_data = [data_col for data_col in column_data if data_col.owner == frappe.session.user or data_col.assigned_to == frappe.session.user]
					else:
						filter_column_data = convert_filter_to_tuple(doctype, column_filters)
						if project is not None and project != "":
							filter_column_data.append(['GP Task', 'project', '=', project])
						if assign_task is not None and len(assign_task) > 0:
							filter_column_data.append(['GP Task', 'assigned_to', 'in', assign_task])
						column_data = frappe.get_list(
							doctype,
							fields=rows,
							filters=filter_column_data,
							order_by=order_by,
							page_length=page_length
						)
						if is_my_task == "true":
							column_data = [data_col for data_col in column_data if data_col.owner == frappe.session.user or data_col.assigned_to == frappe.session.user]
				new_filters = filters.copy()
				new_filters.update({ column_field: kc.get('name') })
				if len(or_filters) > 0:
					filter_all_count = convert_filter_to_tuple(doctype, new_filters)
					if project is not None and project != "":
						filter_all_count.append(['GP Task', 'project', '=', project])
					all_count = len(frappe.get_list(doctype, filters=filter_all_count, or_filters=or_filters))
				else:
					filter_all_count = convert_filter_to_tuple(doctype, new_filters)
					if project is not None and project != "":
						filter_all_count.append(['GP Task', 'project', '=', project])
					all_count = len(frappe.get_list(doctype, filters=filter_all_count))
				kc["all_count"] = all_count
				kc["count"] = len(column_data)
			if order:
				column_data = sorted(
					column_data, key=lambda x: order.index(x.get("name"))
					if x.get("name") in order else len(order)
				)
			data.append({"column": kc, "fields": kanban_fields, "data": column_data})
	fields = frappe.get_meta(doctype).fields
	fields = [field for field in fields if field.fieldtype not in no_value_fields]
	fields = [
		{
			"label": _(field.label),
			"type": field.fieldtype,
			"value": field.fieldname,
			"options": field.options,
		}
		for field in fields
		if field.label and field.fieldname
	]
	std_fields = [
		{"label": "Name", "type": "Data", "value": "name"},
		{"label": "Created On", "type": "Datetime", "value": "creation"},
		{"label": "Last Modified", "type": "Datetime", "value": "modified"},
		{
			"label": "Modified By",
			"type": "Link",
			"value": "modified_by",
			"options": "User",
		},
		{"label": "Assigned To", "type": "Text", "value": "_assign"},
		{"label": "Owner", "type": "Link", "value": "owner", "options": "User"},
		{"label": "Like", "type": "Data", "value": "_liked_by"},
	]
	for field in std_fields:
		if field.get('value') not in rows:
			rows.append(field.get('value'))
		if field not in fields:
			field["label"] = _(field["label"])
			fields.append(field)
	return {
		"data": data,
		"columns": columns,
		"rows": rows,
		"fields": fields,
		"column_field": column_field,
		"title_field": title_field,
		"kanban_columns": kanban_columns,
		"kanban_fields": kanban_fields,
		"page_length": page_length,
		"page_length_count": page_length_count,
		"total_count": len(frappe.get_list(doctype, filters=filters)),
		"row_count": len(data)
	}

@frappe.whitelist(methods=["POST"])
def get_attachments(doctype, name):
	attachments = []
	try:
		attachments = frappe.get_all(
			"File",
			fields=["name", "file_name", "file_url", "creation", "file_type"],
			filters={"attached_to_name": name, "attached_to_doctype": doctype},
		)
		return attachments
	except Exception as e:
		return attachments

@frappe.whitelist(methods=["POST"])
def delete_attachments(doctype, name):
	try:
		attachments = frappe.get_all(
			"File",
			fields=["name", "file_name"],
			filters={"attached_to_name": name, "attached_to_doctype": doctype},
		)
		for attachment in attachments:
			attachment_info = frappe.get_doc('File', attachment.name)
			attachment_info.delete()
		frappe.db.commit()
		return "ok"
	except Exception as e:
		return "error"

@frappe.whitelist()
def delete_all_checklist(task_id):
	try:
		checklists = frappe.get_list('GP CheckList',
			filters={
				'parent': task_id
			},
			fields=['name', 'label']
		)
		for checklist in checklists:
			checklist_doc = frappe.get_doc('GP CheckList', checklist.name)
			checklist_doc.delete()
		frappe.db.commit()
		return "ok"
	except Exception as e:
		return "error"

@frappe.whitelist(methods=["DELETE"])
def delete_task_by_id(name):
	try:
		task_info = frappe.get_doc('GP Task', name)
		if task_info.custom_fields is not None and task_info.custom_fields != "":
			custom_fields = json.loads(task_info.custom_fields)
			if custom_fields['id_reminder'] is not None and custom_fields['id_reminder'] != "":
				reminder_info = frappe.get_doc('GP Reminder', custom_fields['id_reminder'])
				reminder_info.delete()
		notifications = frappe.db.get_list('GP Notification',
			filters={
				'task': name
			},
			fields=['name']
		)
		for notification in notifications:
			notification_info = frappe.get_doc('GP Notification', notification.name)
			notification_info.delete()
		task_info.delete()
		frappe.db.commit()
		return {'status': "ok", 'message': None}
	except Exception as e:
		return {'status': "error", 'message': str(e)}

@frappe.whitelist()
def get_value_by_reference_doctype(reference_doctype, project=None):
	values_by_reference = []
	if project is not None and project != "":
		project_info = frappe.get_doc('GP Project', project)
		if project_info.is_private == 0:
			values_public = frappe.db.get_list(reference_doctype,
				filters={
					'project': project
				},
				fields=['name', 'title']
			)
			for value_public in values_public:
				arr_filter = [val_fil['value'] for val_fil in values_by_reference if val_fil['value'] == value_public.name]
				if len(arr_filter) == 0:
					values_by_reference.append({
						'label': value_public.title,
						'value': value_public.name
					})
	values_public = frappe.db.get_list(reference_doctype,
		filters={
			'owner': frappe.session.user
		},
		fields=['name', 'title']
	)
	for value_public in values_public:
		arr_filter = [val_fil['value'] for val_fil in values_by_reference if val_fil['value'] == value_public.name]
		if len(arr_filter) == 0:
			values_by_reference.append({
				'label': value_public.title,
				'value': value_public.name
			})
	return values_by_reference

@frappe.whitelist()
def get_mypages_by_filter(order_by, search=None, project=None):
	pages = []
	if project is not None and project != "":
		if search is not None and search != "":
			pages = frappe.get_all('GP Page',
				filters = {
					'project': project
				},
				fields=['name','creation','title','content','slug','project','team','modified','owner'],
				or_filters=[
					["title", "LIKE", f'%{search}%'],
					["owner", "LIKE", f'%{search}%']
				],
				order_by=order_by,
				page_length=999
			)
		else:
			pages = frappe.get_all('GP Page',
				filters={
					'project': project
				},
				fields=['name','creation','title','content','slug','project','team','modified','owner'],
				order_by=order_by,
				page_length=999
			)
	else:
		if search is not None and search != "":
			pages = frappe.get_all('GP Page',
				filters = {
					'owner': frappe.session.user
				},
				fields=['name','creation','title','content','slug','project','team','modified','owner'],
				or_filters=[
					["title", "LIKE", f'%{search}%']
				],
				order_by=order_by,
				page_length=999
			)
			page_sources = frappe.get_all('GP Page',
				filters = {
					'owner': frappe.session.user
				},
				fields=['name','creation','title','content','slug','project','team','modified','owner'],
				order_by=order_by,
				page_length=999
			)
			team_sources = get_teams_by_role()
			team_sources = [team.name for team in team_sources if search in team.title]
			for page in page_sources:
				if page.team in team_sources:
					page_filter = [item for item in pages if item.name == page.name]
					if len(page_filter) == 0:
						pages.append(page)
			project_sources = [str(project.name) for project in get_projects_by_role() if search in project.title]
			for page in page_sources:
				if page.project in project_sources:
					page_filter_project = [item for item in pages if item.name == page.name]
					if len(page_filter_project) == 0:
						pages.append(page)
		else:
			pages = frappe.get_all('GP Page',
				filters={
					'owner': frappe.session.user
				},
				fields=['name','creation','title','content','slug','project','team','modified','owner'],
				order_by=order_by,
				page_length=999
			)
	return pages

@frappe.whitelist()
def permission_task(task):
	task_doc = frappe.get_doc('GP Task', task)
	if task_doc.owner == frappe.session.user or task_doc.assigned_to == frappe.session.user:
		return "write"
	elif task_doc.project is not None and task_doc.team is not None and task_doc.project != "" and task_doc.team != "":
		user_doc = frappe.get_doc('User', frappe.session.user)
		arr_role = [_role.role for _role in user_doc.roles]
		if "Gameplan Admin" in arr_role:
			return "write"
		if "Gameplan Member" in arr_role:
			project_doc = frappe.get_doc('GP Project', task_doc.project)
			if project_doc.is_private == 0:
				return "read"
			else:
				team_doc = frappe.get_doc('GP Team', task_doc.team)
				members = team_doc.members
				for member in members:
					if member.user == frappe.session.user:
						if member.role == "member":
							return "read"
						else:
							return "write"
		if "Gameplan Guest" in arr_role:
			return "read"
	return "read"

@frappe.whitelist()
def permission_discussion(discussion):
	discussion_doc = frappe.get_doc('GP Discussion', discussion)
	if discussion_doc.owner == frappe.session.user:
		return "write"
	else:
		user_doc = frappe.get_doc('User', frappe.session.user)
		arr_role = [_role.role for _role in user_doc.roles]
		if "Gameplan Admin" in arr_role:
			return "write"
		if "Gameplan Member" in arr_role:
			project_doc = frappe.get_doc('GP Project', task_doc.project)
			if project_doc.is_private == 0:
				return "read"
			else:
				team_doc = frappe.get_doc('GP Team', task_doc.team)
				members = team_doc.members
				for member in members:
					if member.user == frappe.session.user:
						if member.role == "member":
							return "read"
						else:
							return "write"
		if "Gameplan Guest" in arr_role:
			return "read"

@frappe.whitelist()
def permission_page(page):
	page_doc = frappe.get_doc('GP Page', page)
	if page_doc.owner == frappe.session.user:
		return "write"
	elif page_doc.project is not None and page_doc.team is not None and page_doc.project != "" and page_doc.team != "":
		user_doc = frappe.get_doc('User', frappe.session.user)
		arr_role = [_role.role for _role in user_doc.roles]
		if "Gameplan Admin" in arr_role:
			return "write"
		if "Gameplan Member" in arr_role:
			project_doc = frappe.get_doc('GP Project', task_doc.project)
			if project_doc.is_private == 0:
				return "read"
			else:
				team_doc = frappe.get_doc('GP Team', task_doc.team)
				members = team_doc.members
				for member in members:
					if member.user == frappe.session.user:
						if member.role == "member":
							return "read"
						else:
							return "write"
		if "Gameplan Guest" in arr_role:
			return "read"
	return "read"

@frappe.whitelist(allow_guest=True)
@validate_type
def accept_invitation(key: str = None):
	if not key:
		frappe.throw("Invalid or expired key")

	result = frappe.db.get_all("GP Invitation", filters={"key": key}, pluck="name")
	if not result:
		frappe.throw("Invalid or expired key")

	invitation = frappe.get_doc("GP Invitation", result[0])
	invitation.accept()
	invitation.reload()

	if invitation.status == "Accepted":
		objProject = json.loads(invitation.projects)
		strGuest = frappe.db.get_value('GP Project', objProject[0], "guests")
		objGuest = []
		if strGuest is not None and strGuest != "":
			objGuest = json.loads(strGuest)
		if invitation.email not in objGuest:
			objGuest.append(invitation.email)
		frappe.db.set_value('GP Project', objProject[0], "guests", json.dumps(objGuest))
		#Gửi thông báo tới manage,admin
		user_info = frappe.db.get_value('User', {'email': invitation.email}, ['name'], as_dict=1)
		config_notifications = frappe.db.get_all(
			"GP Config Notification",
			fields=["config_notification"],
			filters={"user": frappe.session.user}
		)
		config_notification = []
		type_notify = []
		if len(config_notifications) == 0:
			configs = random_config_notification()
			doc_config_notification = frappe.new_doc('GP Config Notification')
			doc_config_notification.config_notification = json.dumps(configs)
			doc_config_notification.user = frappe.session.user
			doc_config_notification.insert(ignore_permissions=True)
			frappe.db.commit()
			config_notification = configs
		else:
			config_notification = json.loads(config_notifications[0].config_notification)
		if config_notification[0]["arr_permission"][0]["email"] == True:
			type_notify.append("email")
		if config_notification[0]["arr_permission"][0]["browser"] == True:
			type_notify.append('browser')
		#send_manager_by_invite_guest(type_notify, user_info.name, objProject[0])

		frappe.local.login_manager.login_as(invitation.email)
		frappe.local.response["type"] = "redirect"
		frappe.local.response["location"] = "/g"

@frappe.whitelist()
def get_unsplash_photos(keyword=None):
	from gameplan.unsplash import get_list, get_by_keyword

	if keyword:
		return get_by_keyword(keyword)

	return frappe.cache().get_value("unsplash_photos", generator=get_list)


@frappe.whitelist()
def get_unread_items():
	from frappe.query_builder.functions import Count

	Discussion = frappe.qb.DocType("GP Discussion")
	Visit = frappe.qb.DocType("GP Discussion Visit")
	query = (
		frappe.qb.from_(Discussion)
		.select(Discussion.team, Count(Discussion.team).as_("count"))
		.left_join(Visit)
		.on((Visit.discussion == Discussion.name) & (Visit.user == frappe.session.user))
		.where((Visit.last_visit.isnull()) | (Visit.last_visit < Discussion.last_post_at))
		.groupby(Discussion.team)
	)

	is_guest = gameplan.is_guest()
	if is_guest:
		GuestAccess = frappe.qb.DocType("GP Guest Access")
		project_list = GuestAccess.select(GuestAccess.project).where(GuestAccess.user == frappe.session.user)
		query = query.where(Discussion.project.isin(project_list))

	# pypika doesn't have any API for "FORCE INDEX FOR JOIN"
	sql = query.get_sql()
	sql = sql.replace(
		"LEFT JOIN `tabGP Discussion Visit`", "LEFT JOIN `tabGP Discussion Visit` FORCE INDEX FOR JOIN(discussion_user_index)"
	)
	data = frappe.db.sql(sql, as_dict=1)

	out = {}
	for d in data:
		out[d.team] = d.count
	return out


@frappe.whitelist()
def get_unread_items_by_project(projects):
	from frappe.query_builder.functions import Count

	project_names = frappe.parse_json(projects)
	Discussion = frappe.qb.DocType("GP Discussion")
	Visit = frappe.qb.DocType("GP Discussion Visit")
	query = (
		frappe.qb.from_(Discussion)
		.select(Discussion.project, Count(Discussion.project).as_("count"))
		.left_join(Visit)
		.on((Visit.discussion == Discussion.name) & (Visit.user == frappe.session.user))
		.where((Visit.last_visit.isnull()) | (Visit.last_visit < Discussion.last_post_at))
		.where(Discussion.project.isin(project_names))
		.groupby(Discussion.project)
	)

	data = query.run(as_dict=1)
	out = {}
	for d in data:
		out[d.project] = d.count
	return out


@frappe.whitelist()
def mark_all_notifications_as_read():
	for d in frappe.db.get_all("GP Notification", filters={"to_user": frappe.session.user, "read": 0}, pluck="name"):
		doc = frappe.get_doc("GP Notification", d)
		doc.read = 1
		doc.save(ignore_permissions=True)


@frappe.whitelist()
def recent_projects():
	from frappe.query_builder.functions import Max

	ProjectVisit = frappe.qb.DocType("GP Project Visit")
	Team = frappe.qb.DocType("GP Team")
	Project = frappe.qb.DocType("GP Project")
	Pin = frappe.qb.DocType("GP Pinned Project")
	pinned_projects_query = frappe.qb.from_(Pin).select(Pin.project).where(Pin.user == frappe.session.user)
	projects = (
		frappe.qb.from_(ProjectVisit)
		.select(
			ProjectVisit.project.as_("name"),
			Project.team,
			Project.title.as_("project_title"),
			Team.title.as_("team_title"),
			Project.icon,
			Max(ProjectVisit.last_visit).as_("timestamp"),
		)
		.left_join(Project)
		.on(Project.name == ProjectVisit.project)
		.left_join(Team)
		.on(Team.name == Project.team)
		.groupby(ProjectVisit.project)
		.where(ProjectVisit.user == frappe.session.user)
		.where(ProjectVisit.project.notin(pinned_projects_query))
		.orderby(ProjectVisit.last_visit, order=frappe.qb.desc)
		.limit(12)
	)

	return projects.run(as_dict=1)


@frappe.whitelist()
def active_projects():
	from frappe.query_builder.functions import Count

	Comment = frappe.qb.DocType("GP Comment")
	Discussion = frappe.qb.DocType("GP Discussion")
	CommentCount = Count(Comment.name).as_("comments_count")
	active_projects = (
		frappe.qb.from_(Comment)
		.select(CommentCount, Discussion.project)
		.left_join(Discussion)
		.on(Discussion.name == Comment.reference_name)
		.where(Comment.reference_doctype == "GP Discussion")
		.where(Comment.creation > frappe.utils.add_days(frappe.utils.now(), -70))
		.groupby(Discussion.project)
		.orderby(CommentCount, order=frappe.qb.desc)
		.limit(12)
	).run(as_dict=1)

	projects = frappe.qb.get_query(
		"GP Project",
		fields=["name", "title as project_title", "team", "team.title as team_title", "icon", "modified as timestamp"],
		filters={"name": ("in", [d.project for d in active_projects])},
	).run(as_dict=1)

	active_projects_comment_count = {d.project: d.comments_count for d in active_projects}
	for d in projects:
		d.comments_count = active_projects_comment_count.get(str(d.name), 0)

	projects.sort(key=lambda d: d.comments_count, reverse=True)

	return projects


@frappe.whitelist()
def onboarding(data):
	data = frappe.parse_json(data)
	team = frappe.get_doc(doctype="GP Team", title=data.team).insert()
	frappe.get_doc(doctype="GP Project", team=team.name, title=data.project).insert()
	emails = ", ".join(data.emails)
	invite_by_email(emails, role="Gameplan Member")
	return team.name


@frappe.whitelist(allow_guest=True)
def oauth_providers():
	from frappe.utils.html_utils import get_icon_html
	from frappe.utils.password import get_decrypted_password
	from frappe.utils.oauth import get_oauth2_authorize_url, get_oauth_keys

	out = []
	providers = frappe.get_all(
		"Social Login Key",
		filters={"enable_social_login": 1},
		fields=["name", "client_id", "base_url", "provider_name", "icon"],
		order_by="name",
	)

	for provider in providers:
		client_secret = get_decrypted_password("Social Login Key", provider.name, "client_secret")
		if not client_secret:
			continue

		icon = None
		if provider.icon:
			if provider.provider_name == "Custom":
				icon = get_icon_html(provider.icon, small=True)
			else:
				icon = f"<img src='{provider.icon}' alt={provider.provider_name}>"

		if provider.client_id and provider.base_url and get_oauth_keys(provider.name):
			out.append(
				{
					"name": provider.name,
					"provider_name": provider.provider_name,
					"auth_url": get_oauth2_authorize_url(provider.name, "/g"),
					"icon": icon,
				}
			)
	return out


@frappe.whitelist()
def search(query, start=0):
	from gameplan.search import GameplanSearch

	search = GameplanSearch()
	query = search.clean_query(query)

	query_parts = query.split(" ")
	if len(query_parts) == 1 and not query_parts[0].endswith("*"):
		query = f"{query_parts[0]}*"
	if len(query_parts) > 1:
		query = " ".join([f"%%{q}%%" for q in query_parts])

	result = search.search(
		f"@title|content:({query})", start=start, sort_by="modified desc", highlight=True, with_payloads=True
	)

	comments_by_doctype = {}
	grouped_results = {}
	for d in result.docs:
		doctype, name = d.id.split(":")
		d.doctype = doctype
		d.name = name
		del d.id
		if doctype == "GP Comment":
			comments_by_doctype.setdefault(d.payload["reference_doctype"], []).append(d)
		else:
			d.project = d.payload.get("project")
			d.team = d.payload.get("team")
			del d.payload
			grouped_results.setdefault(doctype, []).append(d)

	discussion_names = [d.payload["reference_name"] for d in comments_by_doctype.get("GP Discussion", [])]
	task_names = [d.payload["reference_name"] for d in comments_by_doctype.get("GP Task", [])]

	if discussion_names:
		for d in frappe.get_all(
			"GP Discussion",
			fields=["name", "title", "last_post_at", "project", "team"],
			filters={"name": ("in", discussion_names)},
		):
			d.doctype = "GP Discussion"
			d.name = cstr(d.name)
			d.content = ""
			d.via_comment = True
			d.modified = d.last_post_at
			for c in comments_by_doctype.get("GP Discussion", []):
				if c.payload["reference_name"] == d.name:
					d.content = c.content
			grouped_results.setdefault("GP Discussion", []).append(d)

	if task_names:
		for d in frappe.get_all(
			"GP Task", fields=["name", "title", "modified", "project", "team"], filters={"name": ("in", task_names)}
		):
			d.doctype = "GP Task"
			d.name = cstr(d.name)
			d.content = ""
			d.via_comment = True
			for c in comments_by_doctype.get("GP Task", []):
				if c.payload["reference_name"] == d.name:
					d.content = c.content
			grouped_results.setdefault("GP Task", []).append(d)

	return {
		"results": grouped_results,
		"total": result.total,
		"duration": result.duration,
	}

@frappe.whitelist()
def get_token():
	return frappe.sessions.get_csrf_token()

@frappe.whitelist(allow_guest=True)
def get_translations():
	if frappe.session.user != "Guest":
		language = frappe.db.get_value("User", frappe.session.user, "language")
	else:
		language = frappe.db.get_single_value("System Settings", "language")

	return get_all_translations(language)

@frappe.whitelist()
def get_config_app_firebase():
	apikey_fcm = frappe.db.get_single_value('GP FCM App', 'apikey')
	authdomain_fcm = frappe.db.get_single_value('GP FCM App', 'authdomain')
	projectid_fcm = frappe.db.get_single_value('GP FCM App', 'projectid')
	storagebucket_fcm = frappe.db.get_single_value('GP FCM App', 'storagebucket')
	messagingsenderid_fcm = frappe.db.get_single_value('GP FCM App', 'messagingsenderid')
	appid_fcm = frappe.db.get_single_value('GP FCM App', 'appid')
	measurementid_fcm = frappe.db.get_single_value('GP FCM App', 'measurementid')
	if apikey_fcm is not None and authdomain_fcm is not None and projectid_fcm is not None and storagebucket_fcm is not None and messagingsenderid_fcm is not None and appid_fcm is not None and measurementid_fcm is not None and apikey_fcm != "" and authdomain_fcm != "" and projectid_fcm != "" and storagebucket_fcm != "" and messagingsenderid_fcm != "" and appid_fcm != "" and measurementid_fcm != "":
		return {
			'apiKey': apikey_fcm,
			'authDomain': authdomain_fcm,
			'projectId': projectid_fcm,
			'storageBucket': storagebucket_fcm,
			'messagingSenderId': messagingsenderid_fcm,
			'appId': appid_fcm,
			'measurementId': measurementid_fcm
		}
	else:
		return None

@frappe.whitelist()
def get_vapid_key_firebase():
	vapid_key_fcm = frappe.db.get_single_value('GP FCM App', 'vapid_key')
	if vapid_key_fcm is not None and vapid_key_fcm != "":
		return vapid_key_fcm
	else:
		return None

@frappe.whitelist()
def is_exist_token():
	tokens = frappe.db.get_list('GP FCM Token',
        filters = {
            'owner': frappe.session.user
        },
        fields=['token', 'owner']
    )
	if len(tokens) > 0:
		return 1
	else:
		return 0

@frappe.whitelist(methods=["POST"])
def token_firebase(token):
	token_doc = frappe.new_doc('GP FCM Token')
	token_doc.token = token
	token_doc.insert()
	frappe.db.commit()

@frappe.whitelist(methods=["GET"])
def get_config_view(doc):
	try:
		objConfig = {}
		view_settings = frappe.get_list('GP View Settings',
			filters={
				'dt': doc,
				'owner': frappe.session.user
			},
			fields=['name', 'dt', 'view_type']
		)
		if len(view_settings) == 0:
			view_setting_doc = frappe.new_doc('GP View Settings')
			view_setting_doc.dt = doc
			view_setting_doc.view_type = "list"
			view_setting_doc.insert()
			frappe.db.commit()
			objConfig['name'] = view_setting_doc.name
			objConfig['view_type'] = view_setting_doc.view_type
		else:
			objConfig['name'] = view_settings[0].name
			objConfig['view_type'] = view_settings[0].view_type
		return objConfig
	except Exception as e:
		return None

@frappe.whitelist(methods=["POST"])
def update_config_view(name, view_type):
	try:
		view_setting = frappe.get_doc('GP View Settings', name)
		view_setting.view_type = view_type
		view_setting.save()
		frappe.db.commit()
		return {'status': "ok", 'message': ""}
	except Exception as e:
		return {'status': "error", 'message': ""}


@frappe.whitelist(methods=["GET"])
def test_notification(title, body):
	send_notification_to_user(title, body)
