from ..services.movie_service import get_aggregate_requests
from flask import render_template
from ..app.app_instance import app
from ..constants.api_constants import API_HEADERS


def fetch_movies(
    api_url: str, headers: dict = API_HEADERS, pages: int = 15, **kwargs
) -> list:
    """Fetches movie data from the API.

    Args:
        api_url (str): The API URL to fetch data from.
        headers (dict, optional): The headers to include in the request.
            Defaults to API_HEADERS.
        pages (int, optional): The number of pages to fetch.
            Defaults to 15.
        **kwargs: Additional parameters to include in the request.

    Returns:
        list: The fetched movie data.
    """
    app.logger.info(f"Fetching data from {api_url} with parameters {kwargs}")
    try:
        movie_data = get_aggregate_requests(
            api_url, headers, pages=pages, **kwargs
        )
        app.logger.info(f"Successfully fetched data from {api_url}")
        return movie_data
    except Exception as e:
        app.logger.error(f"Failed to get data from {api_url}: {e}")
        return []


def render_movies_page(
    movies: list, title: str = "Popular Movies", rated_movies: list = []
) -> str:
    """Renders the index.html template with the provided movie data.

    Args:
        movies (list): The movie data to include in the page.
        title (str, optional): The title to display on the page.
            Defaults to "Popular Movies".
        rated_movies (list, optional): The movies rated by the user.
            Defaults to an empty list.

    Returns:
        str: The rendered template.
    """
    try:
        return render_template(
            "index.html", movies=movies, title=title, rated_movies=rated_movies
        )
    except Exception as e:
        app.logger.error(f"Failed to render template: {e}")
        return render_template(
            "error.html", message="Failed to render template"
        )


def fetch_rated_movies(
    user_api_url: str, headers: dict, session_id: str
) -> list:
    """Fetches the movies rated by the user if the user is logged in.

    Args:
        user_api_url (str): The API URL to fetch data from.
        headers (dict): The headers to include in the request.
        session_id (str): The session ID of the user.

    Returns:
        list: The movies rated by the user, or an empty list if the user
        is not logged in.
    """
    if session_id:
        print("Fetching rated movies")
        try:
            rated_movies = get_aggregate_requests(
                user_api_url, headers, pages=-1, session_id=session_id
            )
            app.logger.info("Successfully fetched rated movies")
            return rated_movies
        except Exception as e:
            app.logger.error(
                f"Failed to get rated movies from {user_api_url}: {e}"
            )
    return []


def handle_movie_route(
    url: str,
    page_title: str,
    rated_movies_url: str,
    session_id: str,
    **kwargs,
) -> str:
    """Handles a movie route. If the page title is not provided, the
    user is redirected to the homepage.

    Args:
        url (str): The API URL to fetch data from.
        page_title (str): The title to display on the page.
        rated_movies_url (str): The API URL to fetch rated movies from.
        session_id (str): The session ID of the user.

    Returns:
        str: The rendered template.
    """
    movies = fetch_movies(url, session_id=session_id, **kwargs)
    rated_movies = fetch_rated_movies(rated_movies_url, API_HEADERS, session_id)
    return render_movies_page(movies, page_title, rated_movies)
