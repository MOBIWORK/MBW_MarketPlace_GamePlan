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

def add_discussion_of_project(type_notify, projectId, discussionId, user_creation):
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
        notify_text = f'{get_fullname(user_creation)} đã tạo thảo luận mới {discussion_doc.title}'
        values_notify = frappe._dict(
            from_user=user_creation,
            to_user=member.user,
            message=notify_text,
            doctype="GP Notification",
            project=discussion_doc.project,
            team=discussion_doc.team,
            discussion=discussionId
        )
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
    for guest in arr_guest:
        guest_info = frappe.get_doc('User', guest)
        notify_text = f'{get_fullname(user_creation)} đã tạo thảo luận mới {discussion_doc.title}'
        values_notify = frappe._dict(
            from_user=user_creation,
            to_user=guest,
            message=notify_text,
            doctype="GP Notification",
            project=discussion_doc.project,
            team=discussion_doc.team,
            discussion=discussionId
        )
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

def add_page_of_project(type_notify, projectId, pageId, user_creation):
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
        notify_text = f'{get_fullname(user_creation)} đã tạo trang mới {page_doc.title}'
        values_notify = frappe._dict(
            from_user=user_creation,
            to_user=member.user,
            message=notify_text,
            doctype="GP Notification",
            project=page_doc.project,
            team=page_doc.team
        )
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
    for guest in arr_guest:
        guest_info = frappe.get_doc('User', guest)
        notify_text = f'{get_fullname(user_creation)} đã tạo trang mới {page_doc.title}'
        values_notify = frappe._dict(
            from_user=user_creation,
            to_user=guest,
            message=notify_text,
            doctype="GP Notification",
            project=page_doc.project,
            team=page_doc.team,
        )
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

def add_comment_owner_discussion(type_notify, discussionId, commentId):
    discusson_doc = frappe.get_doc('GP Discussion', discussionId)
    comment_doc = frappe.get_doc('GP Comment', commentId)
    project_doc = frappe.get_doc('GP Project', discusson_doc.project)
    notify_text = f'{get_fullname(comment_doc.owner)} đã bình luận trong thảo luận {discusson_doc.title}'
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

def add_reaction_owner_discussion(type_notify, discussionId, userReactionId, nameReaction):
    discussion_doc = frappe.get_doc('GP Discussion', discussionId)
    project_doc = frappe.get_doc('GP Project', discussion_doc.project)
    notify_text = f'{get_fullname(userReactionId)} đã thả cảm xúc về thảo luận {discussion_doc.title}'
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

def add_poll_followed_discussion(type_notify, discussionId, pollId, userReceived):
    discussion_doc = frappe.get_doc('GP Discussion', discussionId)
    project_doc = frappe.get_doc('GP Project', discussion_doc.project)
    poll_doc = frappe.get_doc('GP Poll', pollId)
    notify_text = f'{get_fullname(poll_doc.owner)} đã tạo cuộc bình chọn trong thảo luận {discussion_doc.title}'
    user_recipient = frappe.get_doc('User', userReceived)
    user_sender = frappe.get_doc('User', poll_doc.owner)
    values_notify = frappe._dict(
        from_user=poll_doc.owner,
        to_user=userReactionId,
        message=notify_text,
        doctype="GP Notification",
        project=discussion_doc.project,
        team=discussion_doc.team,
        discussion=discussionId
    )
    if frappe.db.exists('GP Notification', values_notify):
        return
    try:
        frappe.get_doc(values_notify).insert()
        frappe.db.commit()
    except Exception as e:
        pass
    if type_notify == "gmail":
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

def close_conclusion_followed_discussion(type_notify, discussionId, userReceived):
    discussion_doc = frappe.get_doc('GP Discussion', discussionId)
    project_doc = frappe.get_doc('GP Project', discussion_doc.project)
    notify_text = f'Thảo luận {discussion_doc.title} đã đóng và có kết luận'
    user_recipient = frappe.get_doc('User', userReceived)
    user_sender = frappe.get_doc('User', discussion_doc.owner)
    values_notify = frappe._dict(
        from_user=discussion_doc.owner,
        to_user=userReceived,
        message=notify_text,
        doctype="GP Notification",
        project=discussion_doc.project,
        team=discussion_doc.team,
        discussion=discussionId
    )
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

def send_notify_by_value(value_notify):
    if frappe.db.exists('GP Notification', value_notify):
        return
    frappe.get_doc(value_notify).insert()
    frappe.db.commit()