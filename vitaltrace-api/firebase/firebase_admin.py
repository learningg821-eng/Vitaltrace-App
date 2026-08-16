import os
import json
import firebase_admin
from firebase_admin import credentials, messaging

if not firebase_admin._apps:
    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    
    if service_account_json:
        service_account_info = json.loads(service_account_json)
        cred = credentials.Certificate(service_account_info)
    else:
        cred = credentials.Certificate("firebase/service-account.json")
    
    firebase_admin.initialize_app(cred)

def send_fcm_notification(
    fcm_token: str,
    title: str,
    body: str,
    data: dict | None = None,
):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data or {},
        token=fcm_token,
    )
    return messaging.send(message)