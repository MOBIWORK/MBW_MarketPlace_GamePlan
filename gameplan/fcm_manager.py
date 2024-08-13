import firebase_admin
from firebase_admin import credentials, messaging
import frappe
from gameplan.utils import init_config_fcm_admin

type_fcm = frappe.db.get_single_value('GP FCM Admin', 'type')
project_id_fcm = frappe.db.get_single_value('GP FCM Admin', 'project_id')
private_key_id_fcm = frappe.db.get_single_value('GP FCM Admin', 'private_key_id')
private_key_fcm = frappe.db.get_single_value('GP FCM Admin', 'private_key')
client_email_fcm = frappe.db.get_single_value('GP FCM Admin', 'client_email')
client_id_fcm = frappe.db.get_single_value('GP FCM Admin', 'client_id')
auth_uri_fcm = frappe.db.get_single_value('GP FCM Admin', 'auth_uri')
token_uri_fcm = frappe.db.get_single_value('GP FCM Admin', 'token_uri')
auth_provider_x509_cert_url_fcm = frappe.db.get_single_value('GP FCM Admin', 'auth_provider_x509_cert_url')
client_x509_cert_url_fcm = frappe.db.get_single_value('GP FCM Admin', 'client_x509_cert_url')
universe_domain_fcm = frappe.db.get_single_value('GP FCM Admin', 'universe_domain')

config_service_account_key = init_config_fcm_admin()
if type_fcm is not None and project_id_fcm is not None and private_key_id_fcm is not None and private_key_fcm is not None and client_email_fcm is not None and client_id_fcm is not None and auth_uri_fcm is not None and token_uri_fcm is not None and auth_provider_x509_cert_url_fcm is not None and client_x509_cert_url_fcm is not None and universe_domain_fcm is not None and type_fcm != "" and project_id_fcm != "" and private_key_id_fcm != "" and private_key_fcm != "" and client_email_fcm != "" and client_id_fcm != "" and auth_uri_fcm != "" and token_uri_fcm != "" and auth_provider_x509_cert_url_fcm != "" and client_x509_cert_url_fcm != "" and universe_domain_fcm != "":
    config_service_account_key = {
        'type': type_fcm,
		'project_id': project_id_fcm,
		'private_key_id': private_key_id_fcm,
		'private_key': private_key_fcm.replace("\\n", "\n"),
		'client_email': client_email_fcm,
		'client_id': client_id_fcm,
		'auth_uri': auth_uri_fcm,
		'token_uri': token_uri_fcm,
		'auth_provider_x509_cert_url': auth_provider_x509_cert_url_fcm,
		'client_x509_cert_url': client_x509_cert_url_fcm,
		'universe_domain': universe_domain_fcm
    }
print("Dòng 33 ", config_service_account_key)
cred = credentials.Certificate(config_service_account_key)
firebase_admin.initialize_app(cred)

def send_notification_to_user(title, body):
    tokens = frappe.db.get_list('GP FCM Token',
        filters = {
            'owner': frappe.session.user
        },
        fields=['token', 'owner']
    )
    token=""
    if len(tokens) == 0:
        return
    else:
        token = tokens[0]['token']
    message = messaging.Message(
        notification = messaging.Notification(
            title = title,
            body = body
        ),
        token = token
    )
    response = messaging.send(message)


