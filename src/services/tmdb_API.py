from ..constants.api_constants import (
    API_HEADERS,
    API_ACCESS_TOKEN,
    API_BASE_URL,
)
import json
import requests


class APIKeyError(Exception):
    pass


class TMDB_API_v3(object):
    URLS = {}
    BASE_PATH = ""
    HEADERS = API_HEADERS
    ACCESS_TOKEN = API_ACCESS_TOKEN
    BASE_URL = API_BASE_URL

    def __init__(self, session_id: str = ""):
        self.session_id = session_id

    def set_session_id(self, session_id: str):
        self.session_id = session_id

    def _get_path(self, key):
        return self.BASE_PATH + self.URLS[key]

    def _get_id_path(self, key):
        return self._get_path(key).format(id=self.id)

    def _get_guest_session_id_path(self, key):
        return self._get_path(key).format(
            guest_session_id=self.guest_session_id
        )

    def _get_credit_id_path(self, key):
        return self._get_path(key).format(credit_id=self.credit_id)

    def _get_media_type_time_window_path(self, key):
        return self._get_path(key).format(
            media_type=self.media_type, time_window=self.time_window
        )

    def _get_tv_id_season_number_path(self, key):
        return self._get_path(key).format(
            tv_id=self.tv_id, season_number=self.season_number
        )

    def _get_tv_id_season_number_episode_number_path(self, key):
        return self._get_path(key).format(
            tv_id=self.tv_id,
            season_number=self.season_number,
            episode_number=self.episode_number,
        )

    def _get_complete_url(self, path):
        return "{base_url}/{path}".format(base_url=self.BASE_URL, path=path)

    def _get_params(self, params):
        if params:
            for key, value in params.items():
                if isinstance(params[key], bool):
                    params[key] = "true" if value is True else "false"
            return params
        return {}

    def _request(self, method, path, params=None, payload=None):
        url = self._get_complete_url(path)
        params = self._get_params(params)

        # Create a new request session if no global session is defined
        if self.session_id is None:
            response = requests.request(
                method,
                url,
                params=params,
                data=json.dumps(payload) if payload else payload,
                headers=self.HEADERS,
            )

        # Use the global requests session the user provided
        else:
            response = requests.request(
                method,
                url,
                params=params,
                data=json.dumps(payload) if payload else payload,
                headers=self.HEADERS,
            )

        response.raise_for_status()
        response.encoding = "utf-8"
        return response.json()

    def _GET(self, path, params=None):
        return self._request("GET", path, params=params)

    def _POST(self, path, params=None, payload=None):
        return self._request("POST", path, params=params, payload=payload)

    def _DELETE(self, path, params=None, payload=None):
        return self._request("DELETE", path, params=params, payload=payload)

    def _set_attrs_to_values(self, response={}):
        """
        Set attributes to dictionary values.

        - e.g.
        >>> from ..services.movies import Movies
        >>> movie = Movies(15)
        >>> response = movie.info()
        >>> movie.title  # instead of response['title']
        """
        if isinstance(response, dict):
            for key in response.keys():
                if not hasattr(self, key) or not callable(getattr(self, key)):
                    setattr(self, key, response[key])
