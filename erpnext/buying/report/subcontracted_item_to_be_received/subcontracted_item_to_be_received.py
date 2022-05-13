# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _


def execute(filters=None):
	if filters.from_date >= filters.to_date:
		frappe.msgprint(_("To Date must be greater than From Date"))

	data = []
	columns = get_columns()
	get_data(data, filters)
	return columns, data


def get_columns():
	return [
		{
			"label": _("Subcontracting Order"),
			"fieldtype": "Link",
			"fieldname": "subcontracting_order",
			"options": "Subcontracting Order",
			"width": 150,
		},
		{"label": _("Date"), "fieldtype": "Date", "fieldname": "date", "hidden": 1, "width": 150},
		{
			"label": _("Supplier"),
			"fieldtype": "Link",
			"fieldname": "supplier",
			"options": "Supplier",
			"width": 150,
		},
		{
			"label": _("Finished Good Item Code"),
			"fieldtype": "Data",
			"fieldname": "fg_item_code",
			"width": 100,
		},
		{"label": _("Item name"), "fieldtype": "Data", "fieldname": "item_name", "width": 100},
		{
			"label": _("Required Quantity"),
			"fieldtype": "Float",
			"fieldname": "required_qty",
			"width": 100,
		},
		{
			"label": _("Received Quantity"),
			"fieldtype": "Float",
			"fieldname": "received_qty",
			"width": 100,
		},
		{"label": _("Pending Quantity"), "fieldtype": "Float", "fieldname": "pending_qty", "width": 100},
	]


def get_data(data, filters):
	sco = get_sco(filters)
	sco_name = [v.name for v in sco]
	sub_items = get_subcontracting_order_item_supplied(sco_name)
	for item in sub_items:
		for order in sco:
			if order.name == item.parent and item.received_qty < item.qty:
				row = {
					"subcontracting_order": item.parent,
					"date": order.transaction_date,
					"supplier": order.supplier,
					"fg_item_code": item.item_code,
					"item_name": item.item_name,
					"required_qty": item.qty,
					"received_qty": item.received_qty,
					"pending_qty": item.qty - item.received_qty,
				}
				data.append(row)


def get_sco(filters):
	record_filters = [
		["supplier", "=", filters.supplier],
		["transaction_date", "<=", filters.to_date],
		["transaction_date", ">=", filters.from_date],
		["docstatus", "=", 1],
	]
	return frappe.get_all(
		"Subcontracting Order", filters=record_filters, fields=["name", "transaction_date", "supplier"]
	)


def get_subcontracting_order_item_supplied(sco):
	return frappe.get_all(
		"Subcontracting Order Item",
		filters=[("parent", "IN", sco)],
		fields=["parent", "item_code", "item_name", "qty", "received_qty"],
	)
