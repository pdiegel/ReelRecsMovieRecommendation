import requests
from typing import Any, Dict, List, Union
import logging
import json


logging.basicConfig(filename="logs.txt", level=logging.INFO)


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


def rate_movie(movie_id, rating, session_id, headers, api_key):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/rating?\
api_key={api_key}"
    headers = {"Content-Type": "application/json;charset=utf-8"}
    data = {"value": rating}  # rating value should be between 0.5 and 10

    query_params = {"session_id": session_id}

    response = requests.post(
        url, headers=headers, params=query_params, data=json.dumps(data)
    )
    print(response.json())

    if response.status_code == 201:
        print(f"Movie {movie_id} rated successfully")
    else:
        print(f"Failed to rate movie: {response.status_code}, {response.text}")
