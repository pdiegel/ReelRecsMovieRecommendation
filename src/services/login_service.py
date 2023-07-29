from flask_login import UserMixin, current_user


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
