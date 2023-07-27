import requests
from typing import Any, Dict, List, Union
import logging
import json
from ..constants.api_constants import MODIFY_WATCHLIST_URL, ACCOUNT_ID
import tmdbsimple as tmdb
from flask import render_template

logging.basicConfig(filename="logs.txt", level=logging.INFO)


def get_movie_pages(pages, func=None, **kwargs):
    if pages == -1:
        response = func(**kwargs)
        pages = response["total_pages"]
        print(pages)

    results = []
    for i in range(1, pages + 1):
        response = func(page=i, **kwargs)
        results.extend(response["results"])

    return results


def get_account_info_pages(session_id, logged_in, movies):
    print(f"Logged in: {logged_in}")

    account_states = []
    for movie in movies:
        account_states.append(
            tmdb.Movies(movie.get("id", "")).account_states(
                session_id=session_id
            )
        )

    return account_states


def render_movie_template(
    title, session_id, func, pages=3, logged_in=False, **kwargs
):
    movies = get_movie_pages(pages, func, **kwargs)
    if logged_in:
        account_states = get_account_info_pages(session_id, logged_in, movies)
    else:
        account_states = []

    return render_template(
        "index.html",
        movies=movies,
        title=title,
        account_states=account_states,
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


def rate_movie(
    movie_id: str,
    rating: str,
    session_id: str,
    headers: dict,
    api_key: str,
) -> None:
    """Rates a movie. The rating value should be between 0.5 and 10.

    Args:
        movie_id (str): Id of the movie to rate.
        rating (str): Rating to give the movie.
        session_id (str): Id of the user's session.
        headers (dict): The headers to send with the request.
        api_key (str): The API key to use.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/rating?\
api_key={api_key}"
    headers = {"Content-Type": "application/json;charset=utf-8"}
    data = {"value": rating}  # rating value should be between 0.5 and 10.0

    query_params = {"session_id": session_id}

    response = requests.post(
        url, headers=headers, params=query_params, data=json.dumps(data)
    )

    if response.status_code == 201:
        print(f"Movie {movie_id} rated successfully")
    else:
        print(f"Failed to rate movie: {response.status_code}, {response.text}")


def watchlist_movie(
    movie_id: int,
    watchlist: str,
    session_id: str,
    headers: dict,
    access_token: str,
):
    """Adds a movie to the user's watchlist.

    Args:
        movie_id (int): Id of the movie to rate.
        watchlist (str): Boolean value indicating whether to add or remove
            the movie from the watchlist.
        session_id (str): Id of the user's session.
        headers (dict): The headers to send with the request.
        api_key (str): The API key to use.
    """
    url = MODIFY_WATCHLIST_URL.format(
        account_id=ACCOUNT_ID, session_id=session_id
    )
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    data = {"media_type": "movie", "media_id": movie_id, "watchlist": watchlist}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(url)

    if response.status_code == 200:
        print(f"Movie {movie_id} removed from watchlist successfully")
    elif response.status_code == 201:
        print(f"Movie {movie_id} added to watchlist successfully")
    else:
        print(
            f"Failed to add movie to watchlist: {response.status_code},\
 {response.text}"
        )
