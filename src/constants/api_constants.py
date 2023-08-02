from dotenv import load_dotenv
import os

# PATHS ================================================================

# ENVIRONMENT VARIABLES ================================================
load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY is not set in .env file")

API_ACCESS_TOKEN = os.getenv("API_ACCESS_TOKEN")
if not API_ACCESS_TOKEN:
    raise ValueError("API_ACCESS_TOKEN is not set in .env file")

ACCOUNT_OBJECT_ID = os.getenv("ACCOUNT_OBJECT_ID")
if not ACCOUNT_OBJECT_ID:
    raise ValueError("ACCOUNT_OBJECT_ID is not set in .env file")

ACCOUNT_ID = os.getenv("ACCOUNT_ID")

# API ENDPOINTS ========================================================
API_BASE_URL = "https://api.themoviedb.org/3/"
API_BASE_URL_V4 = "https://api.themoviedb.org/4/"
API_HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": f"Bearer {API_ACCESS_TOKEN}",
}


def generate_api_url(url, base_url=API_BASE_URL):
    """Generates a full API URL by appending the base URL to the given
    URL.

    Args:
        url (str): The URL to append to the base URL.
        base_url (str, optional): The base URL. Defaults to
            API_BASE_URL.

    Returns:
        str: The full API URL.
    """
    return base_url + url


TOKEN_AUTH_URL = generate_api_url(
    "https://www.themoviedb.org/authenticate/{request_token}?redirect_to=\
{redirect_to}",
    "",
)

RECOMMENDED_MOVIES_URL = generate_api_url(
    "account/{session_id}/movie/\
recommendations?page={page}",
    API_BASE_URL_V4,
)
