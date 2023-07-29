from ..services.tmdb_API import TMDB_API_v3


class Movies(TMDB_API_v3):
    BASE_PATH = "movie"
    GENRES = {
        "action": 28,
        "adventure": 12,
        "animation": 16,
        "comedy": 35,
        "crime": 80,
        "documentary": 99,
        "drama": 18,
        "family": 10751,
        "horror": 27,
    }
    URLS = {
        "details": "/{id}",
        "account_states": "/{id}/account_states",
        "alternative_titles": "/{id}/alternative_titles",
        "changes": "/{id}/changes",
        "credits": "/{id}/credits",
        "external_ids": "/{id}/external_ids",
        "images": "/{id}/images",
        "keywords": "/{id}/keywords",
        "latest": "/latest",
        "lists": "/{id}/lists",
        "recommendations": "/{id}/recommendations",
        "release_dates": "/{id}/release_dates",
        "reviews": "/{id}/reviews",
        "similar": "/{id}/similar",
        "translations": "/{id}/translations",
        "videos": "/{id}/videos",
        "watch_providers": "/{id}/watch/providers",
        "add_rating": "/{id}/rating",
        "delete_rating": "/{id}/rating",
    }

    def __init__(self, id: int = 0):
        super(Movies, self).__init__()
        self.id = id

    def get_details(self, **kwargs) -> dict:
        """Get the primary information about a movie.

        Args:
            language: (optional) ISO 639-1 code.
            append_to_response: (optional) Append requests within the
                same namespace to the response.

        Returns:
            dict: The JSON movie details returned from the API.
        """
        path = self._get_id_path("details")

        response = self._GET(path, kwargs)
        self._set_attrs_to_values(response)
        return response


if __name__ == "__main__":
    movie = Movies(550)
    movie_details = movie.get_details()
    print(movie.title)
