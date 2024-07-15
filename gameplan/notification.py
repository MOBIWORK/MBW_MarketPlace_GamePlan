import frappe
from frappe.utils import get_fullname
from frappe.core.doctype.communication.email import make
from datetime import datetime
import json


def send_manager_by_invite_guest(type_notify, idGuest, idProject):
    user_doc = frappe.get_doc('User', idGuest)
    project_doc = frappe.get_doc('GP Project', idProject)
    members = project_doc.members
    notify_text = f'{get_fullname(idGuest)} đã tham gia dự án {project_doc.title}'
    user_recipients = []
    for member in members:
        if member.user != idGuest:
            member_info = frappe.get_doc("User", member.user)
            roles_of_member = [_role.role for _role in member_info.roles]
            if "Gameplan Admin" in roles_of_member:
                user_recipients.append(member_info.email)
                values_notify = frappe._dict(
                    from_user=idGuest,
                    to_user=member.user,
                    project=idProject,
                    team=project_doc.team,
                    message=notify_text,
                    doctype="GP Notification"
                )
                if frappe.db.exists('GP Notification', values_notify):
                    return
                try:
                    frappe.get_doc(values_notify).insert()
                    frappe.db.commit()
                except Exception as e:
                    pass
    if type_notify == "gmail":
        content_email = f'<p>{get_fullname(idGuest)} đã tham gia dự án {project_doc.title} vào lúc {datetime.now()}</p>'
        make(
            doctype="GP Project",
            name=idProject,
            content = content_email,
            recipients = ','.join(user_recipients),
            send_email = True,
            sender = user_doc.email,
            sender_full_name = "Trợ lý app Team",
            subject = f'[TEAM] {get_fullname(idGuest)} đã tham gia dự án {project_doc.title}'
        )

def send_guest_by_invite_guest(type_notify, idGuest, type_reference, name_reference):
    user_send = frappe.get_doc('User', frappe.session.user)
    user_received = frappe.get_doc('User', idGuest)
    roles_of_received = [_role.role for _role in user_received.roles]
    type_joining = ""
    name_joining = ""
    doctype_reference = ""
    role_of_received = ""
    if "Gameplan Admin" in roles_of_received:
        role_of_received = "Admin"
    elif "Gameplan Member" in roles_of_received:
        role_of_received = "Member"
    elif "Gameplan Guest" in roles_of_received:
        role_of_received = "Guest"
    if type_reference == "team":
        type_joining = "nhóm"
        team_doc = frappe.get_doc('GP Team', name_reference)
        name_joining = team_doc.title
        doctype_reference = "GP Team"
    elif type_reference == "project":
        type_joining = "dự án"
        project_doc = frappe.get_doc('GP Project', name_reference)
        name_joining = project_doc.title
        doctype_reference = "GP Project"
    if type_joining == "" and name_joining == "":
        return
    if frappe.session.user != idGuest:
        notify_text = f'{get_fullname(frappe.session.user)} đã thêm bạn vào {type_joining} {name_joining}'
        values_notify = frappe._dict(
            from_user=frappe.session.user,
            to_user=idGuest,
            message=notify_text,
            doctype="GP Notification"
        )
        if type_reference == "team":
            values_notify.team = name_reference
        elif type_reference == "project":
            project_doc = frappe.get_doc('GP Project', name_reference)
            values_notify.project = name_reference
            values_notify.team = project_doc.team
        if frappe.db.exists('GP Notification', values_notify):
            return
        try:
            frappe.get_doc(values_notify).insert()
            frappe.db.commit()
        except Exception as e:
            pass
        if type_notify == "gmail":
            content_email = f"""
                <div class="mb-2 leading-5 text-gray-600">
                    <span class="font-medium">{ get_fullname(frappe.session.user) }</span>
                    <span> đã thêm bạn vào {type_joining} {name_joining} với vai trò {role_of_received}</span>
                </div>
            """
            make(
                doctype=doctype_reference,
                name=name_reference,
                content = content_email,
                recipients = user_received.email,
                send_email = True,
                sender = user_send.email,
                sender_full_name = user_send.full_name,
                subject = f'[TEAM] {get_fullname(frappe.session.user)} đã thêm bạn vào {type_joining} {name_joining}'
            )

def change_limit_project_team(type_notify, type_reference, name_reference):
    arr_member = []
    arr_guest = []
    type_joining = ""
    name_joining = ""
    doctype_reference = ""
    limit = ""
    if type_reference == "team":
        type_joining = "nhóm"
        team_doc = frappe.get_doc('GP Team', name_reference)
        name_joining = team_doc.title
        doctype_reference = "GP Team"
        arr_member = team_doc.members
        if team_doc.is_private == True:
            limit = "riêng tư"
        else:
            limit = "công khai"
    elif type_reference == "project":
        type_joining = "dự án"
        project_doc = frappe.get_doc('GP Project', name_reference)
        doctype_reference = "GP Project"
        arr_member = project_doc.members
        if project_doc.guests is not None and project_doc.guests != "":
            arr_guest = json.loads(project_doc.guests)
        if project_doc.is_private == True:
            limit = "riêng tư"
        else:
            limit = "công khai"
    for member in arr_member:
        member_info = frappe.get_doc('User', member.user)
        if member.user != frappe.session.user:
            user_sender = frappe.get_doc('User', frappe.session.user)
            notify_text = f'{get_fullname(frappe.session.user)} đã thay đổi {type_joining} {name_joining} thành {type_joining} {limit}'
            values_notify = frappe._dict(
                from_user=frappe.session.user,
                to_user=member.user,
                message=notify_text,
                doctype="GP Notification"
            )
            if type_reference == "team":
                values_notify.team = name_reference
            elif type_reference == "project":
                project_doc = frappe.get_doc('GP Project', name_reference)
                values_notify.project = name_reference
                values_notify.team = project_doc.team
            if frappe.db.exists('GP Notification', values_notify):
                return
            try:
                frappe.get_doc(values_notify).insert()
                frappe.db.commit()
            except Exception as e:
                pass
            if type_notify == "gmail":
                content_email = f"""
                    <div class="mb-2 leading-5 text-gray-600">
                        <span class="font-medium">{ get_fullname(frappe.session.user) }</span>
                        <span> đã thay đổi {type_joining} {name_joining} thành {type_joining} {limit}</span>
                    </div>
                """
                make(
                    doctype=doctype_reference,
                    name=name_reference,
                    content = content_email,
                    recipients = member_info.email,
                    send_email = True,
                    sender = user_sender.email,
                    sender_full_name = user_sender.full_name,
                    subject = f'[TEAM] {get_fullname(frappe.session.user)} đã thay đổi {type_joining} {name_joining}'
                )
    for guest in arr_guest:
        guest_info = frappe.get_doc('User', guest)
        if guest != frappe.session.user:
            user_sender = frappe.get_doc('User', frappe.session.user)
            notify_text = f'{get_fullname(frappe.session.user)} đã thay đổi {type_joining} {name_joining} thành {type_joining} {limit}'
            values_notify = frappe._dict(
                from_user=frappe.session.user,
                to_user=guest,
                message=notify_text,
                doctype="GP Notification"
            )
            if type_reference == "team":
                values_notify.team = name_reference
            elif type_reference == "project":
                project_doc = frappe.get_doc('GP Project', name_reference)
                values_notify.project = name_reference
                values_notify.team = project_doc.team
            if frappe.db.exists('GP Notification', values_notify):
                return
            try:
                frappe.get_doc(values_notify).insert()
                frappe.db.commit()
            except Exception as e:
                pass
            if type_notify == "gmail":
                content_email = f"""
                    <div class="mb-2 leading-5 text-gray-600">
                        <span class="font-medium">{ get_fullname(frappe.session.user) }</span>
                        <span> đã thay đổi {type_joining} {name_joining} thành {type_joining} {limit}</span>
                    </div>
                """
                make(
                    doctype=doctype_reference,
                    name=name_reference,
                    content = content_email,
                    recipients = guest_info.email,
                    send_email = True,
                    sender = user_sender.email,
                    sender_full_name = user_sender.full_name,
                    subject = f'[TEAM] {get_fullname(frappe.session.user)} đã thay đổi {type_joining} {name_joining}'
                )

def change_name_project_team(type_notify, type_reference, name_reference, title_older, title_new):
    arr_member = []
    arr_guest = []
    type_joining = ""
    name_joining = ""
    doctype_reference = ""
    if type_reference == "team":
        type_joining = "nhóm"
        team_doc = frappe.get_doc('GP Team', name_reference)
        name_joining = team_doc.title
        doctype_reference = "GP Team"
        arr_member = team_doc.members
    elif type_reference == "project":
        type_joining = "dự án"
        project_doc = frappe.get_doc('GP Project', name_reference)
        doctype_reference = "GP Project"
        arr_member = project_doc.members
        if project_doc.guests is not None and project_doc.guests != "":
            arr_guest = json.loads(project_doc.guests)
    for member in arr_member:
        member_info = frappe.get_doc('User', member.user)
        if member.user != frappe.session.user:
            user_sender = frappe.get_doc('User', frappe.session.user)
            notify_text = f'{get_fullname(frappe.session.user)} đổi tên {type_joining} {title_older} thành {title_new}'
            values_notify = frappe._dict(
                from_user=frappe.session.user,
                to_user=member.user,
                message=notify_text,
                doctype="GP Notification"
            )
            if type_reference == "team":
                values_notify.team = name_reference
            elif type_reference == "project":
                project_doc = frappe.get_doc('GP Project', name_reference)
                values_notify.project = name_reference
                values_notify.team = project_doc.team
            if frappe.db.exists('GP Notification', values_notify):
                return
            try:
                frappe.get_doc(values_notify).insert()
                frappe.db.commit()
            except Exception as e:
                pass
            if type_notify == "gmail":
                content_email = f"""
                    <div class="mb-2 leading-5 text-gray-600">
                        <span class="font-medium">{ get_fullname(frappe.session.user) }</span>
                        <span> đã đổi tên {type_joining} {title_older} thành {title_new}</span>
                    </div>
                """
                make(
                    doctype=doctype_reference,
                    name=name_reference,
                    content = content_email,
                    recipients = member_info.email,
                    send_email = True,
                    sender = user_sender.email,
                    sender_full_name = user_sender.full_name,
                    subject = f'[TEAM] {get_fullname(frappe.session.user)} đã thay đổi {type_joining} {title_new}'
                )
    for guest in arr_guest:
        guest_info = frappe.get_doc('User', guest)
        if guest != frappe.session.user:
            user_sender = frappe.get_doc('User', frappe.session.user)
            notify_text = f'{get_fullname(frappe.session.user)} đổi tên {type_joining} {title_older} thành {title_new}'
            values_notify = frappe._dict(
                from_user=frappe.session.user,
                to_user=guest,
                message=notify_text,
                doctype="GP Notification"
            )
            if type_reference == "team":
                values_notify.team = name_reference
            elif type_reference == "project":
                project_doc = frappe.get_doc('GP Project', name_reference)
                values_notify.project = name_reference
                values_notify.team = project_doc.team
            if frappe.db.exists('GP Notification', values_notify):
                return
            try:
                frappe.get_doc(values_notify).insert()
                frappe.db.commit()
            except Exception as e:
                pass
            if type_notify == "gmail":
                content_email = f"""
                    <div class="mb-2 leading-5 text-gray-600">
                        <span class="font-medium">{ get_fullname(frappe.session.user) }</span>
                        <span> đã đổi tên {type_joining} {title_older} thành {title_new}</span>
                    </div>
                """
                make(
                    doctype=doctype_reference,
                    name=name_reference,
                    content = content_email,
                    recipients = guest_info.email,
                    send_email = True,
                    sender = user_sender.email,
                    sender_full_name = user_sender.full_name,
                    subject = f'[TEAM] {get_fullname(frappe.session.user)} đã thay đổi {type_joining} {title_new}'
                )

