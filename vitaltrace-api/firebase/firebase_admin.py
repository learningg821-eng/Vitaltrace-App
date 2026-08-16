import firebase_admin
from firebase_admin import credentials, messaging


SERVICE_ACCOUNT_FILE = "firebase/service-account.json"


if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)

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

    response = messaging.send(message)
    return response