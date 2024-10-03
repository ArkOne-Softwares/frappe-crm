# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class CRMNotification(Document):
	def on_update(self):
		pass
		# frappe.publish_realtime("crm_notification")

def notify_user(args):
	"""
	Notify the assigned user
	"""
	args = frappe._dict(args)
	# ArkOne: Commented this so that the notification is sent even if the owner and assigned_to are same
	# if args.owner == args.assigned_to:
	# 	return

	values = frappe._dict(
		doctype="CRM Notification",
		from_user=args.owner,
		to_user=args.assigned_to,
		type=args.notification_type,
		message=args.message,
		notification_text=args.notification_text,
		notification_type_doctype=args.reference_doctype,
		notification_type_doc=args.reference_docname,
		reference_doctype=args.redirect_to_doctype,
		reference_name=args.redirect_to_docname,
		notification_time=args.notification_time if args.notification_time else frappe.utils.now(),
	)

	if frappe.db.exists("CRM Notification", values):
		return
	frappe.get_doc(values).insert(ignore_permissions=True)


def check_and_send_notifications():
	current_time = frappe.utils.now()
	current_user = frappe.session.user

	# Fetch documents where the notification time has passed and the user hasn't been notified yet
	due_notifications = frappe.get_all(
		"CRM Notification",  # Replace with your Doctype name
		filters={
			"notification_time": ["<=", current_time],
			"to_user": current_user,
			"notified": 0  # Only select records where the notification hasn't been sent yet
		},
		fields=["name", "to_user", "notification_time"]
	)

	# Send notifications for each due document
	for record in due_notifications:
		doc = frappe.get_doc("CRM Notification", record["name"])  # Fetch the actual document
		send_scheduled_notification(doc)

def send_scheduled_notification(doc):
    user = doc.recipient  # The user who will receive the notification
    message = f"Reminder: You have an upcoming task scheduled on {doc.notification_time}."

    # Optionally, you can use real-time notifications as well:
    frappe.publish_realtime(
        event="msgprint",
        message=message,
        user=user
    )

    # Mark the document as notified to avoid resending
    doc.notified = 1
    doc.save()