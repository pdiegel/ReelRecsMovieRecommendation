from ..services.movie_service import get_aggregate_requests, clean_data
from flask import render_template
from ..app.app_instance import app
from ..constants.api_constants import API_HEADERS
import requests


def render_movies(
    api_url: str,
    title: str = "Popular Movies",
    pages: int = 5,
    user_api_url: str = "",
    headers: dict = API_HEADERS,
    **kwargs,
) -> str:
    """Fetches movie data from the API and renders the index.html
    template with the data. If the request fails, renders the error.html
    template with a message.

    Args:
        api_url (str): The API URL to fetch data from.
        title (str, optional): The title to display on the page.
            Defaults to "Popular Movies".
        pages (int, optional): The number of pages to fetch.
            Defaults to 5.

    Returns:
        str: The rendered template.
    """

    app.logger.info(f"Fetching data from {api_url} with parameters {kwargs}")
    try:
        print("getting data")
        movie_data = get_aggregate_requests(
            api_url,
            headers,
            pages=pages,
            **kwargs,
        )
        print("got movie data")
        rated_movies = []
        if user_api_url and kwargs.get("session_id"):
            rated_movies = get_user_rated_movies(
                user_api_url, headers, kwargs.get("session_id")
            )
            app.logger.info("Successfully fetched rated movies")
        app.logger.info(f"Successfully fetched data from {api_url}")
        return render_template(
            "index.html",
            movies=movie_data,
            title=title,
            rated_movies=rated_movies,
        )
    except Exception as e:
        app.logger.error(f"Failed to get data from {api_url}: {e}")
        return render_template("error.html", message="Failed to get data")


def get_user_rated_movies(api_url: str, headers: dict, session_id: str):
    rated_movies = get_aggregate_requests(
        api_url,
        headers,
        session_id=session_id,
        pages=5,
    )
    return rated_movies
