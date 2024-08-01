# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from gameplan.search import GameplanSearch


@frappe.whitelist()
def search(query):
	search = GameplanSearch()
	query = search.clean_query(query)

	query_parts = query.split(" ")
	if len(query_parts) == 1 and not query_parts[0].endswith("*"):
		query = f"{query_parts[0]}*"
	if len(query_parts) > 1:
		query = " ".join([f"%%{q}%%" for q in query_parts])

	query = f"@title:({query})"
	result = search.search(query, start=0, sort_by="modified desc", with_payloads=True)

	groups = {}
	for r in result.docs:
		doctype, name = r.id.split(":")
		r.doctype = doctype
		r.name = name

		if doctype == "GP Discussion":
			groups.setdefault("Discussions", []).append(r)
		elif doctype == "GP Task":
			groups.setdefault("Tasks", []).append(r)
		elif doctype == "GP Page":
			groups.setdefault("Pages", []).append(r)

	out = []
	for key in groups:
		out.append({"title": key, "items": groups[key]})
	return out

@frappe.whitelist()
def get_discussion_owner():
	discussions_owner = []
	discussion_list = frappe.db.get_list('GP Discussion',
		filters = {
			'owner': frappe.session.user
		},
		fields = ['name', 'project', 'team', 'status', 'title']
	)
	for discussion in discussion_list:
		discussions_filter = [discussion_fil['name'] for discussion_fil in discussions_owner if discussion_fil['name'] == discussion['name']]
		if len(discussions_filter) == 0:
			discussions_owner.append(discussion)
	projects_list = frappe.db.get_list('GP Project', 
		filters = {
			'is_private': 0
		},
		fields=['name']
	)
	for project in projects_list:
		discussions_by_project = frappe.db.get_list('GP Discussion',
			filters = {
				'project': project.name
			},
			fields = ['name', 'project', 'team', 'status', 'title']
		)
		for discussion_by_project in discussions_by_project:
			discussions_filter = [discussion_fil['name'] for discussion_fil in discussions_owner if discussion_fil['name'] == discussion_by_project['name']]
			if len(discussions_filter) == 0:
				discussions_owner.append(discussion_by_project)
	return discussions_owner

@frappe.whitelist()
def get_page_owner():
	page_owner = []
	page_list = frappe.db.get_list('GP Page',
		filters = {
			'owner': frappe.session.user
		},
		fields = ['name', 'title', 'project', 'team']
	)
	for page in page_list:
		page_filter = [page_fil['name'] for page_fil in page_owner if page_fil['name'] == page['name']]
		if len(page_filter) == 0:
			page_owner.append(page)
	projects_list = frappe.db.get_list('GP Project', 
		filters = {
			'is_private': 0
		},
		fields=['name']
	)
	for project in projects_list:
		pages_by_project = frappe.db.get_list('GP Page',
			filters = {
				'project': project.name
			},
			fields = ['name', 'title', 'project', 'team']
		)
		for page_by_project in pages_by_project:
			pages_filter = [page_fil['name'] for page_fil in page_owner if page_fil['name'] == page_by_project['name']]
			if len(pages_filter) == 0:
				page_owner.append(page_by_project)
	return page_owner


