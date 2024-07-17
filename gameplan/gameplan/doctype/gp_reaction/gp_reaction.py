# Copyright (c) 2022, Frappe Technologies Pvt Ltd and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class GPReaction(Document):
	def after_insert(self):
		print("Dòng 9 ", self)
