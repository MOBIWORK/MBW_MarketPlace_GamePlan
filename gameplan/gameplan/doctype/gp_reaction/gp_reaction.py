# Copyright (c) 2022, Frappe Technologies Pvt Ltd and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from gameplan.notification import add_reaction_owner_discussion

class GPReaction(Document):
	def before_save(self):
		if self.parenttype == "GP Discussion":
			add_reaction_owner_discussion(self.parent, self.user, self.emoji)
