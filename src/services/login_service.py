import requests
from flask import redirect
from flask_login import UserMixin, current_user
from ..constants.api_constants import (
    TOKEN_AUTH_URL,
    RESPONSE_TOKEN_REQUEST_URL,
    SESSION_ID_URL,
)


def login_to_tmdb(headers: str = "", api_key: str = "", next=""):
    response = requests.get(
        RESPONSE_TOKEN_REQUEST_URL.format(api_key=api_key), headers=headers
    )
    if response.status_code != 200:
        return redirect("/error")
    data = response.json()
    request_token = data.get("request_token", "")

    return ""


def create_session(
    request_token: str,
    headers: str = "",
    api_key: str = "",
) -> redirect:
    url = SESSION_ID_URL.format(api_key=api_key, request_token=request_token)
    response = requests.get(
        url,
        headers=headers,
    )
    return response.json()


def get_session_id():
    if current_user.is_authenticated:
        session_id = current_user.id
        return session_id
    print("User is not logged in")
    return ""


class User(UserMixin):
    def __init__(self, session_id, username=""):
        self.id = session_id
        self.username = username
