import frappe
from crm.fcrm.doctype.crm_notification.crm_notification import notify_user


@frappe.whitelist()
def add_followup(type, notification_time, notification_text, reference_type, reference_name, reason):
    """
    Save a follow-up notification for the assigned user.
    """
    notify_user({
        "owner": frappe.session.user,
        "assigned_to": frappe.session.user,
        "notification_type": type if type else "Lead",
        "message": notification_text,
        "notification_text": notification_text,
        "reference_doctype": reference_type,
        "reference_docname": reference_name,
        "redirect_to_doctype": reference_type,
        "redirect_to_docname": reference_name,
        "notification_time": notification_time
    })

    doc = frappe.new_doc("CRM Follow Up")
    doc.to_user = frappe.session.user
    doc.type = type
    doc.notification_time = notification_time
    doc.notification_text = notification_text
    doc.reference_doctype = reference_type
    doc.reference_name = reference_name
    doc.reason = reason
    doc.insert(ignore_permissions=True)
    
    crm_doc = frappe.get_doc(reference_type, reference_name)
    crm_doc.next_contact_date = notification_time
    crm_doc.save(ignore_permissions=True)
