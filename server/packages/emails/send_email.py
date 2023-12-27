from typing import Dict

import resend

from settings import app_settings


def send_email(params: Dict):
    resend.api_key = app_settings.RESEND_API_KEY
    return resend.Emails.send(params)
