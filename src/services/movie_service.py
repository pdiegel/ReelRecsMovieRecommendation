import requests
from typing import Any, Dict, List, Union
import logging
from ..constants.api_constants import (
    API_HEADERS,
)
import tmdbsimple as tmdb
from flask import render_template

logging.basicConfig(filename="logs.txt", level=logging.INFO)


def get_movie_pages(pages, func=None, **kwargs):
    if pages == -1:
        response = func(**kwargs)
        pages = response["total_pages"]

    results = []
    for i in range(1, pages + 1):
        response = func(page=i, **kwargs)
        results.extend(response["results"])

    return results


def get_account_info_pages(account: tmdb.Account) -> Dict[str, Any]:
    rated_movies = get_movie_pages(-1, account.rated_movies)
    watchlist_movies = get_movie_pages(-1, account.watchlist_movies)
    favorite_movies = get_movie_pages(-1, account.favorite_movies)
    account_states = {
        "rated": rated_movies,
        "watchlist": watchlist_movies,
        "favorite": favorite_movies,
    }
    return account_states


def render_movie_template(
    title, account, func=None, pages=3, logged_in=False, **kwargs
):
    if func is not None:
        movies = get_movie_pages(pages, func, **kwargs)
    else:
        movies = kwargs.get("movies", [])

    if logged_in:
        account_states = get_account_info_pages(account)
    else:
        account_states = {}

    return render_template(
        "index.html",
        movies=movies,
        title=title,
        rated_movies=account_states.get("rated", []),
        watchlist_movies=account_states.get("watchlist", []),
        favorite_movies=account_states.get("favorite", []),
    )


def clean_data(
    data: Union[Dict[str, Any], List[Any], Any]
) -> Union[Dict[str, Any], List[Any], Any]:
    """Recursively removes any keys or values that are None from a
    dictionary or list.

    Args:
        data (Union[Dict[str, Any], List[Any], Any]): The data to clean.

    Returns:
        Union[Dict[str, Any], List[Any], Any]: The cleaned data.
    """
    if isinstance(data, dict):
        return {k: clean_data(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [clean_data(v) for v in data if v is not None]
    else:
        return data


def get_aggregate_requests(
    url: str, headers: dict, pages: int = 1, **kwargs
) -> List[Dict[str, Any]]:
    """Fetches data from an API endpoint that supports pagination.
    The data is fetched from the endpoint for each page and aggregated
    into a single list.

    Args:
        url (str): The API endpoint URL.
        headers (dict): The headers to send with the request.
        pages (int, optional): The number of pages to fetch.

    Returns:
        List[Dict[str, Any]]: The aggregated data.
    """
    if pages == -1:
        response = requests.get(url.format(page=1, **kwargs), headers=headers)
        data = clean_data(response.json())
        pages = data["total_pages"]

    results = []
    for page in range(1, pages + 1):
        try:
            response = requests.get(
                url.format(page=page, **kwargs), headers=headers
            )
            response.raise_for_status()
            data = clean_data(response.json())
            results.extend(data["results"])
        except requests.RequestException as e:
            logging.error(f"Failed to fetch data from {url}: {e}")
        except ValueError as e:
            logging.error(f"Failed to parse JSON data from {url}: {e}")
    return results


def fetch_movies(
    api_url: str, app, headers: dict = API_HEADERS, pages: int = 15, **kwargs
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
