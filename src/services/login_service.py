import requests
from flask import redirect
from flask_login import UserMixin, current_user


def get_response_token(headers: str = "", api_key: str = ""):
    response = requests.get(
        f"https://api.themoviedb.org/3/authentication/token/new?api_key={api_key}",
        headers=headers,
    )
    if response.status_code != 200:
        return redirect("/error")
    data = response.json()
    request_token = data.get("request_token", "")
    direct = redirect(
        f"https://www.themoviedb.org/authenticate/{request_token}?redirect_to=http://127.0.0.1:5000/create_session",
    )  # replace with the API's actual login URL
    return request_token, direct


def create_session(
    request_token: str,
    headers: str = "",
    api_key: str = "",
) -> redirect:
    url = f"https://api.themoviedb.org/3/authentication/session/new?\
api_key={api_key}&request_token={request_token}"
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
