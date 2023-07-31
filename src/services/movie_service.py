import logging
from typing import Any, Callable, Dict, List, Union

import requests
import tmdbsimple as tmdb
from flask import Flask, render_template

from ..constants.api_constants import API_HEADERS

logging.basicConfig(filename="logs.txt", level=logging.INFO)


def get_movie_pages(
    pages: int,
    func: Callable = None,
    **kwargs,
) -> List[Dict[str, Any]]:
    """Fetches data from an API endpoint that supports pagination.

    Args:
        pages (int): Number of pages to fetch.
        func (Callable, optional): Function to call. Defaults to None.

    Returns:
        List[Dict[str, Any]]: The aggregated data.
    """
    if pages == -1:
        response = func(**kwargs)
        pages = response["total_pages"]

    results = []
    for i in range(1, pages + 1):
        response = func(page=i, **kwargs)
        results.extend(response["results"])

    return results


def get_account_info_pages(account: tmdb.Account) -> Dict[str, Any]:
    """Gets the account states for the user.

    Args:
        account (tmdb.Account): The account to get the states for.

    Returns:
        Dict[str, Any]: The account states.
    """
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
    title: str,
    account: tmdb.Account,
    func: Callable = None,
    pages: int = 3,
    logged_in: bool = False,
    **kwargs,
) -> str:
    """Renders the movie template.

    Args:
        title (str): The title of the page.
        account (tmdb.Account): The account to get the states for.
        func (Callable, optional): The function to call.
            Defaults to None.
        pages (int, optional): The number of pages to fetch.
            Defaults to 3.
        logged_in (bool, optional): Whether the user is logged in.
            Defaults to False.

    Returns:
        str: The rendered template.
    """
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
    url: str,
    headers: dict,
    pages: int = 1,
    **kwargs,
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
    api_url: str,
    app: Flask,
    headers: dict = API_HEADERS,
    pages: int = 5,
    **kwargs,
) -> list:
    """Fetches movie data from the TMDB API.

    Args:
        api_url (str): The API endpoint URL.
        app (Flask): The Flask app.
        headers (dict, optional): The headers to send with the request.
            Defaults to API_HEADERS.
        pages (int, optional): The number of pages to fetch.
            Defaults to 5.

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


def render_movie_details_page(
    movie_id: str,
    account: tmdb.Account,
    logged_in: bool = False,
    **kwargs,
):
    movie = tmdb.Movies(movie_id)
    movie_details = movie.info()
    account_states = {}
    if logged_in:
        session_id = account.session_id
        account_states = movie.account_states(session_id=session_id)
    return render_template(
        "movie_details.html",
        movie_details=movie_details,
        account_states=account_states,
    )
