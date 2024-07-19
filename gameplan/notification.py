import frappe
from frappe.utils import get_fullname
from frappe.core.doctype.communication.email import make
from datetime import datetime
from gameplan.utils import get_config_notification_by_user
import json


def send_manager_by_invite_guest(type_notifys, idGuest, idProject):
    user_doc = frappe.get_doc('User', idGuest)
    project_doc = frappe.get_doc('GP Project', idProject)
    members = project_doc.members
    notify_text = f"""
        <div class="text-gray-700">
            <span class="font-medium text-gray-900">{ get_fullname(idGuest) }</span>
            <span> đã tham gia dự án</span>
            <span class="font-medium text-gray-900"> {project_doc.title}</span>
        </div>
    """
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
                send_notify_by_value(values_notify)
    if "email" in type_notifys:
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
        frappe.db.commit()

def send_guest_by_invite_guest(type_notifys, idGuest, type_reference, name_reference):
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
        notify_text = f"""
            <div class="text-gray-700">
                <span class="font-medium text-gray-900">{ get_fullname(frappe.session.user) }</span>
                <span> đã thêm bạn vào {type_joining}</span>
                <span class="font-medium text-gray-900"> {name_joining}</span>
            </div>
        """
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
        send_notify_by_value(values_notify)
        if "email" in type_notifys:
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
            frappe.db.commit()

def change_limit_project_team(type_reference, name_reference):
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
            notify_text = f"""
                <div class="text-gray-700">
                    <span class="font-medium text-gray-900">{ get_fullname(frappe.session.user) }</span>
                    <span> đã thay đổi {type_joining}</span>
                    <span class="font-medium text-gray-900"> {name_joining}</span>
                    <span> thành {type_joining}</span>
                    <span class="font-medium text-gray-900"> {limit}</span>
                </div>
            """
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
            send_notify_by_value(values_notify)
            type_notifys = []
            config_notification = get_config_notification_by_user(member_info)
            if config_notification[1]["arr_permission"][1]["email"] == True:
                type_notifys.append("email")
            if config_notification[1]["arr_permission"][1]["browser"] == True:
                type_notifys.append('browser')
            if "email" in type_notifys:
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
                frappe.db.commit()
    for guest in arr_guest:
        guest_info = frappe.get_doc('User', guest)
        if guest != frappe.session.user:
            user_sender = frappe.get_doc('User', frappe.session.user)
            notify_text = f"""
                <div class="text-gray-700">
                    <span class="font-medium text-gray-900">{ get_fullname(frappe.session.user) }</span>
                    <span> đã thay đổi {type_joining}</span>
                    <span class="font-medium text-gray-900"> {name_joining}</span>
                    <span> thành {type_joining}</span>
                    <span class="font-medium text-gray-900"> {limit}</span>
                </div>
            """
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
            send_notify_by_value(values_notify)
            type_notifys = []
            config_notification = get_config_notification_by_user(guest_info)
            if config_notification[1]["arr_permission"][1]["email"] == True:
                type_notifys.append("email")
            if config_notification[1]["arr_permission"][1]["browser"] == True:
                type_notifys.append('browser')
            if "email" in type_notifys:
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
                frappe.db.commit()

def change_name_project_team(type_reference, name_reference, title_older, title_new):
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
            notify_text = f"""
                <div class="text-gray-700">
                    <span class="font-medium text-gray-900">{ get_fullname(frappe.session.user) }</span>
                    <span> đổi tên {type_joining}</span>
                    <span class="font-medium text-gray-900"> {title_older}</span>
                    <span> thành</span>
                    <span class="font-medium text-gray-900"> {title_new}</span>
                </div>
            """
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
            send_notify_by_value(values_notify)
            type_notifies = []
            config_notification = get_config_notification_by_user(member_info)
            if config_notification[1]["arr_permission"][3]["email"] == True:
                type_notifies.append("email")
            if config_notification[1]["arr_permission"][3]["browser"] == True:
                type_notifies.append("browser")
            if "email" in type_notifies:
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
                frappe.db.commit()
    for guest in arr_guest:
        guest_info = frappe.get_doc('User', guest)
        if guest != frappe.session.user:
            user_sender = frappe.get_doc('User', frappe.session.user)
            notify_text = f"""
                <div class="text-gray-700">
                    <span class="font-medium text-gray-900">{ get_fullname(frappe.session.user) }</span>
                    <span> đổi tên {type_joining}</span>
                    <span class="font-medium text-gray-900"> {title_older}</span>
                    <span> thành</span>
                    <span class="font-medium text-gray-900"> {title_new}</span>
                </div>
            """
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
            send_notify_by_value(values_notify)
            type_notifies = []
            config_notification = get_config_notification_by_user(guest_info)
            if config_notification[1]["arr_permission"][3]["email"] == True:
                type_notifies.append("email")
            if config_notification[1]["arr_permission"][3]["browser"] == True:
                type_notifies.append("browser")
            if "email" in type_notifies:
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
                frappe.db.commit()

def add_discussion_of_project(projectId, discussionId, user_creation):
    arr_member = []
    arr_guest = []
    project_doc = frappe.get_doc('GP Project', projectId)
    discussion_doc = frappe.get_doc('GP Discussion', discussionId)
    arr_member = project_doc.members
    user_sender = frappe.get_doc('User', user_creation)
    if project_doc.guests is not None and project_doc.guests != "":
        arr_guest = json.loads(project_doc.guests)
    for member in arr_member:
        member_info = frappe.get_doc('User', member.user)
        notify_text = f"""
            <div class="text-gray-700">
                <span class="font-medium text-gray-900">{ get_fullname(user_creation) }</span>
                <span> đã tạo thảo luận mới</span>
                <span class="font-medium text-gray-900"> {discussion_doc.title}</span>
            </div>
        """
        values_notify = frappe._dict(
            from_user=user_creation,
            to_user=member.user,
            message=notify_text,
            doctype="GP Notification",
            project=discussion_doc.project,
            team=discussion_doc.team,
            discussion=discussionId
        )
        send_notify_by_value(values_notify)
        type_notifies = []
        config_notification = get_config_notification_by_user(member_info)
        if config_notification[2]["arr_permission"][0]["email"] == True:
            type_notifies.append("email")
        if config_notification[2]["arr_permission"][0]["browser"] == True:
            type_notifies.append("browser")
        if "email" in type_notifies:
            content_email = f"""
                <div class="mb-2 leading-5 text-gray-600">
                    <div>
                        <span>Dự án </span>
                        <span>{project_doc.title}:</span>
                    </div>
                    <div>{get_fullname(user_creation)} đã tạo thảo luận mới {discussion_doc.title}</div>
                </div>
            """
            make(
                doctype="GP Discussion",
                name=discussionId,
                content = content_email,
                recipients = member_info.email,
                send_email = True,
                sender = user_sender.email,
                sender_full_name = user_sender.full_name,
                subject = f'[TEAM] {get_fullname(user_creation)} đã tạo thảo luận mới {discussion_doc.title}'
            )
            frappe.db.commit()
    for guest in arr_guest:
        guest_info = frappe.get_doc('User', guest)
        notify_text = f"""
            <div class="text-gray-700">
                <span class="font-medium text-gray-900">{ get_fullname(user_creation) }</span>
                <span> đã tạo thảo luận mới</span>
                <span class="font-medium text-gray-900"> {discussion_doc.title}</span>
            </div>
        """
        values_notify = frappe._dict(
            from_user=user_creation,
            to_user=guest,
            message=notify_text,
            doctype="GP Notification",
            project=discussion_doc.project,
            team=discussion_doc.team,
            discussion=discussionId
        )
        send_notify_by_value(values_notify)
        type_notifies = []
        config_notification = get_config_notification_by_user(guest_info)
        if config_notification[2]["arr_permission"][0]["email"] == True:
            type_notifies.append("email")
        if config_notification[2]["arr_permission"][0]["browser"] == True:
            type_notifies.append("browser")
        if "email" in type_notifies:
            content_email = f"""
                <div class="mb-2 leading-5 text-gray-600">
                    <div>
                        <span>Dự án </span>
                        <span>{project_doc.title}:</span>
                    </div>
                    <div>{get_fullname(user_creation)} đã tạo thảo luận mới {discussion_doc.title}</div>
                </div>
            """
            make(
                doctype="GP Discussion",
                name=discussionId,
                content = content_email,
                recipients = guest_info.email,
                send_email = True,
                sender = user_sender.email,
                sender_full_name = user_sender.full_name,
                subject = f'[TEAM] {get_fullname(user_creation)} đã tạo thảo luận mới {discussion_doc.title}'
            )
            frappe.db.commit()

def add_page_of_project(projectId, pageId, user_creation):
    arr_member = []
    arr_guest = []
    project_doc = frappe.get_doc('GP Project', projectId)
    page_doc = frappe.get_doc('GP Page', pageId)
    arr_member = project_doc.members
    user_sender = frappe.get_doc('User', user_creation)
    if project_doc.guests is not None and project_doc.guests != "":
        arr_guest = json.loads(project_doc.guests)
    for member in arr_member:
        member_info = frappe.get_doc('User', member.user)
        notify_text = f"""
            <div class="text-gray-700">
                <span class="font-medium text-gray-900">{ get_fullname(user_creation) }</span>
                <span> đã tạo trang mới</span>
                <span class="font-medium text-gray-900"> {page_doc.title}</span>
            </div>
        """
        values_notify = frappe._dict(
            from_user=user_creation,
            to_user=member.user,
            message=notify_text,
            doctype="GP Notification",
            project=page_doc.project,
            team=page_doc.team
        )
        send_notify_by_value(values_notify)
        type_notifies = []
        config_notification = get_config_notification_by_user(member_info)
        if config_notification[2]["arr_permission"][1]["email"] == True:
            type_notifies.append("email")
        if config_notification[2]["arr_permission"][1]["browser"] == True:
            type_notifies.append("browser")
        if "email" in type_notifies:
            content_email = f"""
                <div class="mb-2 leading-5 text-gray-600">
                    <div>
                        <span>Dự án </span>
                        <span>{project_doc.title}:</span>
                    </div>
                    <div>{get_fullname(user_creation)} đã tạo trang mới {page_doc.title}</div>
                </div>
            """
            make(
                doctype="GP Page",
                name=pageId,
                content = content_email,
                recipients = member_info.email,
                send_email = True,
                sender = user_sender.email,
                sender_full_name = user_sender.full_name,
                subject = f'[TEAM] {get_fullname(user_creation)} đã tạo trang mới {page_doc.title}'
            )
            frappe.db.commit()
    for guest in arr_guest:
        guest_info = frappe.get_doc('User', guest)
        notify_text = f"""
            <div class="text-gray-700">
                <span class="font-medium text-gray-900">{ get_fullname(user_creation) }</span>
                <span> đã tạo trang mới</span>
                <span class="font-medium text-gray-900"> {page_doc.title}</span>
            </div>
        """
        values_notify = frappe._dict(
            from_user=user_creation,
            to_user=guest,
            message=notify_text,
            doctype="GP Notification",
            project=page_doc.project,
            team=page_doc.team,
        )
        send_notify_by_value(values_notify)
        config_notification = get_config_notification_by_user(guest_info)
        type_notifies = []
        if config_notification[2]["arr_permission"][1]["email"] == True:
            type_notifies.append("email")
        if config_notification[2]["arr_permission"][1]["browser"] == True:
            type_notifies.append("browser")
        if "email" in type_notifies:
            content_email = f"""
                <div class="mb-2 leading-5 text-gray-600">
                    <div>
                        <span>Dự án </span>
                        <span>{project_doc.title}:</span>
                    </div>
                    <div>{get_fullname(user_creation)} đã tạo trang mới {page_doc.title}</div>
                </div>
            """
            make(
                doctype="GP Page",
                name=pageId,
                content = content_email,
                recipients = guest_info.email,
                send_email = True,
                sender = user_sender.email,
                sender_full_name = user_sender.full_name,
                subject = f'[TEAM] {get_fullname(user_creation)} đã tạo trang mới {discussion_doc.title}'
            )
            frappe.db.commit()

def add_comment_owner_discussion(type_notifies, discussionId, commentId):
    discusson_doc = frappe.get_doc('GP Discussion', discussionId)
    comment_doc = frappe.get_doc('GP Comment', commentId)
    project_doc = frappe.get_doc('GP Project', discusson_doc.project)
    notify_text = f"""
        <div class="text-gray-700">
            <span class="font-medium text-gray-900">{ get_fullname(comment_doc.owner) }</span>
            <span> đã bình luận trong thảo luận</span>
            <span class="font-medium text-gray-900"> {discusson_doc.title}</span>
        </div>
    """
    user_recipient = frappe.get_doc('User', discusson_doc.owner)
    user_sender = frappe.get_doc('User', comment_doc.owner)
    values_notify = frappe._dict(
        from_user=comment_doc.owner,
        to_user=discusson_doc.owner,
        message=notify_text,
        doctype="GP Notification",
        project=discusson_doc.project,
        team=discusson_doc.team,
        discussion=discussionId
    )
    send_notify_by_value(values_notify)
    if "email" in type_notifies:
        content_email = f"""
            <div class="mb-2 leading-5 text-gray-600">
                <div>
                    <span>Dự án </span>
                    <span>{project_doc.title}</span>
                </div>
                <div>{get_fullname(comment_doc.owner)} đã bình luận trong thảo luận {discusson_doc.title} với nội dung chi tiết như sau:</div>
                <div>{comment_doc.content}</div>
            </div>
            """
        make(
            doctype="GP Comment",
            name=commentId,
            content = content_email,
            recipients = user_recipient.email,
            send_email = True,
            sender = user_sender.email,
            sender_full_name = user_sender.full_name,
            subject = f'[TEAM] {get_fullname(comment_doc.owner)} đã bình luận trong thảo luận {discusson_doc.title}'
        )
        frappe.db.commit()

def add_reaction_owner_discussion(type_notifies, discussionId, userReactionId, nameReaction):
    discussion_doc = frappe.get_doc('GP Discussion', discussionId)
    project_doc = frappe.get_doc('GP Project', discussion_doc.project)
    notify_text = f"""
        <div class="text-gray-700">
            <span class="font-medium text-gray-900">{ get_fullname(userReactionId) }</span>
            <span> đã thả cảm xúc về thảo luận</span>
            <span class="font-medium text-gray-900"> {discussion_doc.title}</span>
        </div>
    """
    user_recipient = frappe.get_doc('User', discussion_doc.owner)
    user_sender = frappe.get_doc('User', userReactionId)
    values_notify = frappe._dict(
        from_user=userReactionId,
        to_user=discussion_doc.owner,
        message=notify_text,
        doctype="GP Notification",
        project=discussion_doc.project,
        team=discussion_doc.team,
        discussion=discussionId
    )
    send_notify_by_value(values_notify)
    if "email" in type_notifies:
        content_email = f"""
            <div class="mb-2 leading-5 text-gray-600">
                <div>
                    <span>Dự án </span>
                    <span>{project_doc.title}</span>
                </div>
                <div>{get_fullname(userReactionId)} đã thả cảm xúc {nameReaction} vào thảo luân {discussion_doc.title}</div>
            </div>
            """
        make(
            doctype="GP Discussion",
            name=discussionId,
            content = content_email,
            recipients = user_recipient.email,
            send_email = True,
            sender = user_sender.email,
            sender_full_name = user_sender.full_name,
            subject = f'[TEAM] {get_fullname(userReactionId)} thả cảm xúc về thảo luận {discussion_doc.title}'
        )
        frappe.db.commit()

def add_comment_followed_discussion(arr_user, discussionId, commentId):
    discussion_doc = frappe.get_doc('GP Discussion', discussionId)
    comment_doc = frappe.get_doc('GP Comment', commentId)
    project_doc = frappe.get_doc('GP Project', discussion_doc.project)
    user_sender = frappe.get_doc('User', comment_doc.owner)
    notify_text = f"""
        <div class="text-gray-700">
            <span class="font-medium text-gray-900">{ get_fullname(comment_doc.owner) }</span>
            <span> đã bình luận trong thảo luận</span>
            <span class="font-medium text-gray-900"> {discusson_doc.title}</span>
        </div>
    """
    for id_user in arr_user:
        if id_user != comment_doc.owner:
            user_recipient = frappe.get_doc('User', id_user)
            values_notify = frappe._dict(
                from_user=comment_doc.owner,
                to_user=id_user,
                message=notify_text,
                doctype="GP Notification",
                project=discusson_doc.project,
                team=discusson_doc.team,
                discussion=discussionId
            )
            config_notification = get_config_notification_by_user(user_recipient)
            type_notifies = []
            if config_notification[3]["arr_permission"][2]["email"] == True:
                type_notifies.append("email")
            if config_notification[3]["arr_permission"][2]["browser"] == True:
                type_notifies.append("browser")
            send_notify_by_value(values_notify)
            if "email" in type_notifies:
                content_email = f"""
                    <div class="mb-2 leading-5 text-gray-600">
                        <div>
                            <span>Dự án </span>
                            <span>{project_doc.title}</span>
                        </div>
                        <div>{get_fullname(comment_doc.owner)} đã bình luận trong thảo luận {discusson_doc.title} với nội dung chi tiết như sau:</div>
                        <div>{comment_doc.content}</div>
                    </div>
                    """
                make(
                    doctype="GP Comment",
                    name=commentId,
                    content = content_email,
                    recipients = user_recipient.email,
                    send_email = True,
                    sender = user_sender.email,
                    sender_full_name = user_sender.full_name,
                    subject = f'[TEAM] {get_fullname(comment_doc.owner)} đã bình luận trong thảo luận {discusson_doc.title}'
                )
                frappe.db.commit()

def add_poll_followed_discussion(arr_user, discussionId, pollId):
    discussion_doc = frappe.get_doc('GP Discussion', discussionId)
    project_doc = frappe.get_doc('GP Project', discussion_doc.project)
    poll_doc = frappe.get_doc('GP Poll', pollId)
    notify_text = f"""
        <div class="text-gray-700">
            <span class="font-medium text-gray-900">{ get_fullname(poll_doc.owner) }</span>
            <span> đã tạo cuộc bình chọn trong thảo luận</span>
            <span class="font-medium text-gray-900"> {discussion_doc.title}</span>
        </div>
    """
    user_sender = frappe.get_doc('User', poll_doc.owner)
    for id_user in arr_user:
        if id_user != poll_doc.owner:
            user_recipient = frappe.get_doc('User', id_user)
            values_notify = frappe._dict(
                from_user=poll_doc.owner,
                to_user=id_user,
                message=notify_text,
                doctype="GP Notification",
                project=discussion_doc.project,
                team=discussion_doc.team,
                discussion=discussionId
            )
            send_notify_by_value(values_notify)
            config_notification = get_config_notification_by_user(user_recipient)
            type_notifies = []
            if config_notification[3]["arr_permission"][3]["email"] == True:
                type_notifies.append("email")
            if config_notification[3]["arr_permission"][3]["browser"] == True:
                type_notifies.append("browser")
            if "email" in type_notifies:
                option_poll_content = ''
                pollOptions = poll_doc.options
                for option in pollOptions:
                    option_poll_content += f"""
                        <li>{option.title}</li>
                    """
                content_email = f"""
                    <div class="mb-2 leading-5 text-gray-600">
                        <div>
                            <span>Dự án </span>
                            <span>{project_doc.title}:</span>
                        </div>
                        <div>{get_fullname(poll_doc.owner)} đã tạo cuộc bình chọn trong thảo luận {discussion_doc.title}</div>
                        <div>{poll_doc.title}</div>
                        <ul>{option_poll_content}</ul>
                    </div>
                    """
                make(
                    doctype="GP Discussion",
                    name=discussionId,
                    content = content_email,
                    recipients = user_recipient.email,
                    send_email = True,
                    sender = user_sender.email,
                    sender_full_name = user_sender.full_name,
                    subject = f'[TEAM] {get_fullname(poll_doc.owner)} đã tạo cuộc bình chọn trong thảo luận {discussion_doc.title}'
                )
                frappe.db.commit()

def close_conclusion_followed_discussion(arr_user, discussionId):
    discussion_doc = frappe.get_doc('GP Discussion', discussionId)
    project_doc = frappe.get_doc('GP Project', discussion_doc.project)
    notify_text = f"""
        <div class="text-gray-700">
            <span>Thảo luận </span>
            <span class="font-medium text-gray-900">{ discussion_doc.title }</span>
            <span> đã đóng và có kết luận</span>
        </div>
    """
    user_sender = frappe.get_doc('User', discussion_doc.owner)
    for id_user in arr_user:
        if id_user != discussion_doc.owner:
            user_recipient = frappe.get_doc('User', id_user)
            values_notify = frappe._dict(
                from_user=discussion_doc.owner,
                to_user=id_user,
                message=notify_text,
                doctype="GP Notification",
                project=discussion_doc.project,
                team=discussion_doc.team,
                discussion=discussionId
            )
            send_notify_by_value(value_notify)
            config_notification = get_config_notification_by_user(user_recipient)
            type_notifies = []
            if config_notification[3]["arr_permission"][4]["email"] == True:
                type_notifies.append("email")
            if config_notification[3]["arr_permission"][4]["browser"] == True:
                type_notifies.append("browser")
            if "email" in type_notifies:
                content_email = f"""
                    <div class="mb-2 leading-5 text-gray-600">
                        <div>
                            <span>Dự án </span>
                            <span>{project_doc.title}</span>
                        </div>
                        <div>Thảo luận {discussion_doc.title} đã đóng và có kết luận</div>
                        <div>{discussion_doc.conclusion}</div>
                    </div>
                    """
                make(
                    doctype="GP Discussion",
                    name=discussionId,
                    content = content_email,
                    recipients = user_recipient.email,
                    send_email = True,
                    sender = user_sender.email,
                    sender_full_name = user_sender.full_name,
                    subject = f'[TEAM] Thảo luận {discussion_doc.title} đã đóng và có kết luận'
                )
                frappe.db.commit()

def assign_to_someone_task(projectId, taskId, assigner, recipient, title_task):
    notify_text = f"""
        <div class="text-gray-700">
            <span class="font-medium text-gray-900">{ get_fullname(assigner) }</span>
            <span> đã giao cho bạn nhiệm vụ</span>
            <span class="font-medium text-gray-900"> {title_task}</span>
        </div>
    """
    project_info = frappe.db.get_value('GP Project', projectId, ['title', 'team'], as_dict=1)
    values_notify = frappe._dict(
        from_user=assigner,
        to_user=recipient,
        message=notify_text,
        doctype="GP Notification",
        project=projectId,
        team=project_info.team,
        task=taskId,
        is_assign_task=True
    )
    send_notify_by_value(values_notify)
    user_recipient = frappe.get_doc('User', recipient)
    user_sender = frappe.get_doc('User', assigner)
    config_notification = get_config_notification_by_user(user_recipient)
    type_notifies = []
    if config_notification[4]["arr_permission"][0]["email"] == True:
        type_notifies.append("email")
    if config_notification[4]["arr_permission"][0]["browser"] == True:
        type_notifies.append("browser")
    if "email" in type_notifies:
        content_email = f"""
            <div class="mb-2 leading-5 text-gray-600">
                <div>
                    <span>Dự án </span>
                    <span>{project_info.title}</span>
                </div>
                <div>{get_fullname(assigner)} đã giao cho bạn nhiệm vụ {title_task}</div>
            </div>
        """
        make(
            doctype="GP Task",
            name=taskId,
            content = content_email,
            recipients = user_recipient.email,
            send_email = True,
            sender = user_sender.email,
            sender_full_name = user_sender.full_name,
            subject = f'[TEAM] Bạn có nhiệm vụ mới trong dự án {project_info.title}'
        )
        frappe.db.commit()

def change_status_owner_task(taskId, userChange, statusNew):
    task_info = frappe.db.get_value('GP Task', taskId, ['title', 'status', 'project', 'owner'], as_dict=1)
    project_info = frappe.db.get_value('GP Project', task_info.project, ['title', 'team'], as_dict=1)
    notify_text = f"""
        <div class="text-gray-700">
            <span class="font-medium text-gray-900">{ get_fullname(userChange) }</span>
            <span> đã cập nhật trạng thái nhiệm vụ</span>
            <span class="font-medium text-gray-900"> {task_info.title}</span>
            <span> từ</span>
            <span class="font-medium text-gray-900"> {task_info.status}</span>
            <span> qua</span>
            <span class="font-medium text-gray-900">{statusNew}</span>
        </div>
    """
    values_notify = frappe._dict(
        from_user=userChange,
        to_user=task_info.owner,
        message=notify_text,
        doctype="GP Notification",
        project=task_info.project,
        team=project_info.team,
        task=taskId
    )
    send_notify_by_value(values_notify)
    user_recipient = frappe.get_doc('User', task_info.owner)
    user_sender = frappe.get_doc('User', userChange)
    config_notification = get_config_notification_by_user(user_recipient)
    type_notifies = []
    if config_notification[4]["arr_permission"][1]["email"] == True:
        type_notifies.append("email")
    if config_notification[4]["arr_permission"][1]["browser"] == True:
        type_notifies.append("browser")
    if "email" in type_notifies:
        content_email = f"""
            <div class="mb-2 leading-5 text-gray-600">
                <div>
                    <span>Dự án </span>
                    <span>{project_info.title}</span>
                </div>
                <div>{get_fullname(userChange)} đã cập nhật trạng thái nhiệm vụ {task_info.title} từ {task_info.status} qua {statusNew}</div>
            </div>
        """
        make(
            doctype="GP Task",
            name=taskId,
            content = content_email,
            recipients = user_recipient.email,
            send_email = True,
            sender = user_sender.email,
            sender_full_name = user_sender.full_name,
            subject = f'[TEAM] {get_fullname(userChange)} đã cập nhật trạng thái nhiệm vụ {project_info.title}'
        )
        frappe.db.commit()

def change_assignee_to_older(taskId, new_assignee):
    task_info = frappe.db.get_value('GP Task', taskId, ['title', 'assigned_to', 'project', 'owner'], as_dict=1)
    project_info = frappe.db.get_value('GP Project', task_info.project, ['title', 'team'], as_dict=1)
    notify_text = f"""
        <div class="text-gray-700">
            <span>Nhiệm vụ</span>
            <span class="font-medium text-gray-900"> {task_info.title}</span>
            <span> thay đổi người phụ trách từ bạn qua</span>
            <span class="font-medium text-gray-900"> {get_fullname(new_assignee)}</span>
        </div>
    """
    values_notify = frappe._dict(
        from_user=task_info.owner,
        to_user=task_info.assigned_to,
        message=notify_text,
        doctype="GP Notification",
        project=task_info.project,
        team=project_info.team,
        task=taskId
    )
    send_notify_by_value(values_notify)
    user_recipient = frappe.get_doc('User', task_info.assigned_to)
    user_sender = frappe.get_doc('User', task_info.owner)
    config_notification = get_config_notification_by_user(user_recipient)
    type_notifies = []
    if config_notification[4]["arr_permission"][2]["email"] == True:
        type_notifies.append("email")
    if config_notification[4]["arr_permission"][2]["browser"] == True:
        type_notifies.append("browser")
    if "email" in type_notifies:
        content_email = f"""
            <div class="mb-2 leading-5 text-gray-600">
                <div>
                    <span>Dự án </span>
                    <span>{project_info.title}</span>
                </div>
                <div>Nhiệm vụ {task_info.title} thay đổi người phụ trách từ bạn qua {get_fullname(new_assignee)}</div>
            </div>
        """
        make(
            doctype="GP Task",
            name=taskId,
            content = content_email,
            recipients = user_recipient.email,
            send_email = True,
            sender = user_sender.email,
            sender_full_name = user_sender.full_name,
            subject = f'[TEAM] Nhiệm vụ {task_info.title} thay đổi người phụ trách'
        )
        frappe.db.commit()

def change_due_date_to_assignee(taskId, newDueDate):
    task_info = frappe.db.get_value('GP Task', taskId, ['title', 'assigned_to', 'project', 'owner', 'due_date'], as_dict=1)
    project_info = frappe.db.get_value('GP Project', task_info.project, ['title', 'team'], as_dict=1)
    notify_text = f"""
        <div class="text-gray-700">
            <span>Nhiệm vụ</span>
            <span class="font-medium text-gray-900"> {task_info.title}</span>
            <span> thay đổi hạn chót từ</span>
            <span class="font-medium text-gray-900"> {task_info.due_date}</span>
            <span> qua</span>
            <span class="font-medium text-gray-900"> {newDueDate}</span>
        </div>
    """
    values_notify = frappe._dict(
        from_user=task_info.owner,
        to_user=task_info.assigned_to,
        message=notify_text,
        doctype="GP Notification",
        project=task_info.project,
        team=project_info.team,
        task=taskId
    )
    send_notify_by_value(values_notify)
    user_recipient = frappe.get_doc('User', task_info.assigned_to)
    user_sender = frappe.get_doc('User', task_info.owner)
    config_notification = get_config_notification_by_user(user_recipient)
    type_notifies = []
    if config_notification[4]["arr_permission"][3]["email"] == True:
        type_notifies.append("email")
    if config_notification[4]["arr_permission"][3]["browser"] == True:
        type_notifies.append("browser")
    if "email" in type_notifies:
        content_email = f"""
            <div class="mb-2 leading-5 text-gray-600">
                <div>
                    <span>Dự án </span>
                    <span>{project_info.title}</span>
                </div>
                <div>Nhiệm vụ {task_info.title} thay đổi hạn chót từ {task_info.due_date} qua {newDueDate}</div>
            </div>
        """
        make(
            doctype="GP Task",
            name=taskId,
            content = content_email,
            recipients = user_recipient.email,
            send_email = True,
            sender = user_sender.email,
            sender_full_name = user_sender.full_name,
            subject = f'[TEAM] Nhiệm vụ {task_info.title} thay đổi hạn chót'
        )
        frappe.db.commit()

def change_priority_to_assignee(taskId, newPriority):
    task_info = frappe.db.get_value('GP Task', taskId, ['title', 'assigned_to', 'project', 'owner', 'priority'], as_dict=1)
    project_info = frappe.db.get_value('GP Project', task_info.project, ['title', 'team'], as_dict=1)
    notify_text = f"""
        <div class="text-gray-700">
            <span>Nhiệm vụ</span>
            <span class="font-medium text-gray-900"> {task_info.title}</span>
            <span> thay đổi mức ưu tiên từ</span>
            <span class="font-medium text-gray-900"> {task_info.priority}</span>
            <span> qua</span>
            <span class="font-medium text-gray-900"> {newPriority}</span>
        </div>
    """
    values_notify = frappe._dict(
        from_user=task_info.owner,
        to_user=task_info.assigned_to,
        message=notify_text,
        doctype="GP Notification",
        project=task_info.project,
        team=project_info.team,
        task=taskId
    )
    send_notify_by_value(values_notify)
    user_recipient = frappe.get_doc('User', task_info.assigned_to)
    user_sender = frappe.get_doc('User', task_info.owner)
    config_notification = get_config_notification_by_user(user_recipient)
    type_notifies = []
    if config_notification[4]["arr_permission"][4]["email"] == True:
        type_notifies.append("email")
    if config_notification[4]["arr_permission"][4]["browser"] == True:
        type_notifies.append("browser")
    if "email" in type_notifies:
        content_email = f"""
            <div class="mb-2 leading-5 text-gray-600">
                <div>
                    <span>Dự án </span>
                    <span>{project_info.title}</span>
                </div>
                <div>Nhiệm vụ {task_info.title} thay đổi mức ưu tiên từ {task_info.priority} qua {newPriority}</div>
            </div>
        """
        make(
            doctype="GP Task",
            name=taskId,
            content = content_email,
            recipients = user_recipient.email,
            send_email = True,
            sender = user_sender.email,
            sender_full_name = user_sender.full_name,
            subject = f'[TEAM] Nhiệm vụ {task_info.title} thay đổi mức ưu tiên'
        )
        frappe.db.commit()

def vote_poll_by_someone(pollId, userVote, option):
    poll_info = frappe.db.get_value('GP Poll', pollId, ['title', 'discussion', 'owner'], as_dict=1)
    if poll_info.owner == userVote:
        return
    discussion_info = frappe.db.get_value('GP Discussion', poll_info.discussion, ['project', 'team', 'title'], as_dict=1)
    project_info = frappe.db.get_value('GP Project', discussion_info.project, ['title', 'team'], as_dict=1)
    notify_text = f"""
        <div class="text-gray-700">
            <span class="font-medium text-gray-900">{get_fullname(userVote)}</span>
            <span> đã bình chọn</span>
            <span class="font-medium text-gray-900"> {option}</span>
            <span> trong cuộc bình chọn</span>
            <span class="font-medium text-gray-900"> {poll_info.title}</span>
        </div>
    """
    values_notify = frappe._dict(
        from_user=userVote,
        to_user=poll_info.owner,
        message=notify_text,
        doctype="GP Notification",
        project=discussion_info.project,
        team=discussion_info.team,
        discussion=poll_info.discussion
    )
    send_notify_by_value(values_notify)
    user_recipient = frappe.get_doc('User', poll_info.owner)
    user_sender = frappe.get_doc('User', userVote)
    config_notification = get_config_notification_by_user(user_recipient)
    type_notifies = []
    if config_notification[6]["arr_permission"][0]["email"] == True:
        type_notifies.append("email")
    if config_notification[6]["arr_permission"][0]["browser"] == True:
        type_notifies.append("browser")
    if "email" in type_notifies:
        content_email = f"""
            <div class="mb-2 leading-5 text-gray-600">
                <div>
                    <span>Dự án </span>
                    <span>{project_info.title}</span>
                    <span> - </span>
                    <span>{poll_info.title}</span>
                </div>
                <div>{get_fullname(userVote)} đã bình chọn {option}</div>
            </div>
        """
        make(
            doctype="GP Discussion",
            name=poll_info.discussion,
            content = content_email,
            recipients = user_recipient.email,
            send_email = True,
            sender = user_sender.email,
            sender_full_name = user_sender.full_name,
            subject = f'[TEAM] {get_fullname(userVote)} đã tham gia cuộc bình chọn {poll_info.title}'
        )
        frappe.db.commit()

def close_poll(pollId):
    poll_doc = frappe.get_doc('GP Poll', pollId)
    user_poll = frappe.db.get_value('GP Poll', pollId, 'owner')
    discussion_info = frappe.db.get_value('GP Discussion', poll_doc.discussion, ['project', 'team', 'title'], as_dict=1)
    project_info = frappe.db.get_value('GP Project', discussion_info.project, ['title', 'team'], as_dict=1)
    votes = poll_doc.votes
    for vote in votes:
        if vote.user != user_poll:
            notify_text = f"""
                <div class="text-gray-700">
                    <span>Cuộc bình chọn</span>
                    <span class="font-medium text-gray-900"> {poll_doc.title}</span>
                    <span> đã đóng và có kết quả</span>
                </div>
            """
            values_notify = frappe._dict(
                from_user=user_poll,
                to_user=vote.user,
                message=notify_text,
                doctype="GP Notification",
                project=discussion_info.project,
                team=discussion_info.team,
                discussion=poll_doc.discussion
            )
            send_notify_by_value(values_notify)
            user_recipient = frappe.get_doc('User', vote.user)
            user_sender = frappe.get_doc('User', user_poll)
            config_notification = get_config_notification_by_user(user_recipient)
            type_notifies = []
            if config_notification[6]["arr_permission"][1]["email"] == True:
                type_notifies.append("email")
            if config_notification[6]["arr_permission"][1]["browser"] == True:
                type_notifies.append("browser")
            if "email" in type_notifies:
                content_email = f"""
                    <div class="mb-2 leading-5 text-gray-600">
                        <div>
                            <span>Dự án </span>
                            <span>{project_info.title}</span>
                            <span> - </span>
                            <span>{discussion_info.title}</span>
                        </div>
                        <div>Cuộc bình chọn {poll_doc.title} đã kết thúc với kết quả như sau:</div>
                    </div>
                """
                make(
                    doctype="GP Discussion",
                    name=poll_doc.discussion,
                    content = content_email,
                    recipients = user_recipient.email,
                    send_email = True,
                    sender = user_sender.email,
                    sender_full_name = user_sender.full_name,
                    subject = f'[TEAM] Cuộc bình chọn {poll_doc.title} đã đóng và có kết quả'
                )
                frappe.db.commit()

def send_notify_by_value(value_notify):
    if frappe.db.exists('GP Notification', value_notify):
        return
    frappe.get_doc(value_notify).insert()
    frappe.db.commit()
    frappe.publish_realtime("gp_notification")