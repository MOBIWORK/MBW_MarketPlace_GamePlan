import firebase_admin
from firebase_admin import credentials, messaging
import frappe
from gameplan.utils import init_config_fcm_admin

# Lấy giá trị từ database
# fcm_admin_values = {
#     'type': frappe.db.get_single_value('GP FCM Admin', 'type'),
#     'project_id': frappe.db.get_single_value('GP FCM Admin', 'project_id'),
#     'private_key_id': frappe.db.get_single_value('GP FCM Admin', 'private_key_id'),
#     'private_key': frappe.db.get_single_value('GP FCM Admin', 'private_key'),
#     'client_email': frappe.db.get_single_value('GP FCM Admin', 'client_email'),
#     'client_id': frappe.db.get_single_value('GP FCM Admin', 'client_id'),
#     'auth_uri': frappe.db.get_single_value('GP FCM Admin', 'auth_uri'),
#     'token_uri': frappe.db.get_single_value('GP FCM Admin', 'token_uri'),
#     'auth_provider_x509_cert_url': frappe.db.get_single_value('GP FCM Admin', 'auth_provider_x509_cert_url'),
#     'client_x509_cert_url': frappe.db.get_single_value('GP FCM Admin', 'client_x509_cert_url'),
#     'universe_domain': frappe.db.get_single_value('GP FCM Admin', 'universe_domain')
# }

# Kiểm tra nếu tất cả giá trị đều tồn tại và không rỗng
# if all(fcm_admin_values.values()):
#     fcm_admin_values['private_key'] = fcm_admin_values['private_key'].replace("\\n", "\n")
#     config_service_account_key = fcm_admin_values
# else:
#     config_service_account_key = init_config_fcm_admin()

if not firebase_admin._apps:
    config_service_account_key = init_config_fcm_admin()

    # Khởi tạo Firebase Admin SDK với chứng chỉ
    cred = credentials.Certificate(config_service_account_key)
    firebase_admin.initialize_app(cred)

def send_notification_to_user(title, body):
    tokens = frappe.db.get_list('GP FCM Token', filters={'owner': frappe.session.user}, fields=['token'])

    if not tokens:
        return

    token = tokens[0]['token']

    # Tạo thông báo
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=token
    )

    # Gửi thông báo và trả về kết quả
    response = messaging.send(message)
