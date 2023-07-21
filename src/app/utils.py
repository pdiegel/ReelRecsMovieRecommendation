from helpers.misc_funcs import get_aggregate_requests
from flask import render_template
from main import app
from constants import API_HEADERS


def render_movies(
    api_url: str,
    title: str = "Popular Movies",
    pages: int = 5,
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
        movie_data = get_aggregate_requests(
            api_url,
            API_HEADERS,
            pages=pages,
            **kwargs,
        )
        app.logger.info(f"Successfully fetched data from {api_url}")
        return render_template("index.html", movies=movie_data, title=title)
    except Exception as e:
        app.logger.error(f"Failed to get data from {api_url}: {e}")
        return render_template("error.html", message="Failed to get data")
