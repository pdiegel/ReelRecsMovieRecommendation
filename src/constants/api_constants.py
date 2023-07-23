from dotenv import load_dotenv
import os

# PATHS ================================================================
STATIC_FOLDER = os.path.abspath("./src/static")
TEMPLATES_FOLDER = os.path.abspath("./src/templates")

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

# API ENDPOINTS ========================================================
API_BASE_URL = "https://api.themoviedb.org/3/"
API_BASE_URL_V4 = "https://api.themoviedb.org/4/"
API_HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": f"Bearer {API_ACCESS_TOKEN}",
}
GENRE_SEARCH_URL = (
    API_BASE_URL + "discover/movie?with_genres={genres}&page={page}"
)


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


MOVIE_RECOMMENDATIONS_URL = (
    f"{API_BASE_URL}account/{ACCOUNT_OBJECT_ID}/movie/recommendations"
)
POPULAR_MOVIES_URL = generate_api_url("movie/popular?page={page}")

COOKING_MOVIES_URL = generate_api_url(
    "discover/movie?sort_by=popularity\
.desc&vote_count.gte=15&with_keywords=18293%7C6808%7C10637&page={page}"
)

COOKING_TV_URL = generate_api_url(
    "discover/tv?sort_by=popularity.desc&\
with_keywords=18293%7C6808%7C10637&page={page}"
)

RECOMMENDED_MOVIES_URL = generate_api_url(
    "account/{session_id}/movie/\
recommendations?page={page}",
    API_BASE_URL_V4,
)

RATED_MOVIES_URL = generate_api_url(
    "account/{session_id}/movie/rated", API_BASE_URL_V4
)
