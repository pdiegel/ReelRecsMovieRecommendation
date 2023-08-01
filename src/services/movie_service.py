import logging
from typing import Any, Callable, Dict, List, Union

import tmdbsimple as tmdb
from flask import render_template

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler("logs.txt")
handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)

logger.addHandler(handler)


def get_pages(
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
    try:
        if pages == -1:
            response = func(**kwargs)
            pages = response.get("total_pages", 1)

        results = []
        for i in range(1, pages + 1):
            response = func(page=i, **kwargs)
            results.extend(clean_data(response.get("results", [])))

        return results
    except Exception as e:
        logger.error(f"Error in get_pages: {str(e)}")
        return []


def get_account_states(account: tmdb.Account) -> Dict[str, Any]:
    """Gets the account states for the user.

    Args:
        account (tmdb.Account): The account to get the states for.

    Returns:
        Dict[str, Any]: The account states.
    """
    methods = [
        account.rated_movies,
        account.watchlist_movies,
        account.favorite_movies,
    ]
    keys = ["rated", "watchlist", "favorite"]

    account_states = {
        key: get_pages(-1, method) for key, method in zip(keys, methods)
    }

    return account_states


def render_template_page(
    title: str,
    account: tmdb.Account,
    func: Callable = None,
    template_name: str = "index.html",
    pages: int = 5,
    logged_in: bool = False,
    **kwargs,
) -> str:
    """Renders the movie template.

    Args:
        title (str): The title of the page.
        account (tmdb.Account): The account to get the states for.
        func (Callable, optional): The function to call.
            Defaults to None.
        template_name (str, optional): The name of the template.
            Defaults to "index.html".
        pages (int, optional): The number of pages to fetch.
            Defaults to 5.
        logged_in (bool, optional): Whether the user is logged in.
            Defaults to False.

    Returns:
        str: The rendered template.
    """
    movies = (
        get_pages(pages, func, **kwargs) if func else kwargs.get("movies", [])
    )

    account_states = get_account_states(account) if logged_in else {}

    return render_template(
        template_name,
        movies=movies,
        title=title,
        rated_movies=account_states.get("rated", []),
        watchlist_movies=account_states.get("watchlist", []),
        favorite_movies=account_states.get("favorite", []),
        account_states=account_states,
        movie_cast=kwargs.get("movie_cast", []),
        media_items=kwargs.get("media_items", []),
        person_info=kwargs.get("person_info", []),
        person_portraits=kwargs.get("person_portraits", []),
        person_tagged_images=kwargs.get("person_tagged_images", []),
        person_movie_credits=kwargs.get("person_movie_credits", []),
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
