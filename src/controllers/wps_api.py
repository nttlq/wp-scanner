import os
import json
from pathlib import Path

from dotenv import load_dotenv
import requests


class WpsApi:
    __slots__ = ("__token", "__url", "__header", "__requests_to_api_remaining")

    def __init__(self, token=None):
        self.__token: str = self.__set_token(token)
        self.__url: str = "https://wpscan.com/api/v3/"
        self.__header = self.__set_header()
        self.__requests_to_api_remaining = self.__get_requests_to_api_remaining()

        self.__check_requests_to_api_remaining()

    @property
    def header(self) -> dict[str, str]:
        return self.__header

    def __set_header(self) -> dict[str, str]:
        header = {"Authorization": f"Token token={self.token}"}

        return header

    @property
    def url(self) -> str:
        return self.__url

    @property
    def token(self) -> str:
        return self.__token

    def __set_token(self, token: str) -> str:
        if token is not None:
            if len(token) != 43:
                raise ValueError("INVALID TOKEN")
            return token
        token: str = os.environ.get("WPS_API_TOKEN")
        if not token:
            raise MissingTokenError("TOKEN NOT FOUND")

        return token

    @property
    def requests_to_api_remaining(self) -> int:
        return self.__requests_to_api_remaining

    def __check_requests_to_api_remaining(self) -> bool:
        if self.requests_to_api_remaining <= 0:
            raise RateLimitExceededError("NO REQUESTS REMAINING")
        return True

    def __get_requests_to_api_remaining(self) -> int:
        slug: str = "status"
        get_status_url: str = self.url + slug
        res = requests.get(get_status_url, headers=self.header)

        self.__check_status_code(res.status_code)

        result: str = res.text
        result: dict = json.loads(result)
        result: int = result.get("requests_remaining")

        return result

    def __check_status_code(self, status_code) -> bool:
        if status_code != 200:
            if status_code == 429:
                raise TooManyRequestsError("TOO MANY REQUESTS")
            if status_code == 401:
                raise AuthenticationError("TOKEN EXPIRED OR INVALID")

        return True

    def get_vulnerabilities_by_wp_version(self, version: int) -> list[dict]:
        slug: str = f"wordpresses/{version}"
        url: str = self.url + slug
        res = requests.get(url, headers=self.header)

        self.__check_status_code(res.status_code)

        result: str = res.text
        result: dict = json.loads(result)
        for _, info in result.items():
            vulnerabilities = info.get("vulnerabilities", [])

        return vulnerabilities

    def get_vulnerabilities_by_plugin(self, plugin: str) -> list[dict]:
        slug: str = f"plugins/{plugin}"
        url: str = self.url + slug
        res = requests.get(url, headers=self.header)

        self.__check_status_code(res.status_code)

        result: str = res.text
        result: dict = json.loads(result)

        if result.get("status") == "plugin not found":
            raise ValueError("PLUGIN NOT FOUND")

        for _, info in result.items():
            vulnerabilities = info.get("vulnerabilities", [])

        return vulnerabilities

    def get_vulnerabilities_by_theme(self, theme: str) -> list[dict]:
        slug: str = f"themes/{theme}"
        url: str = self.url + slug
        res = requests.get(url, headers=self.header)

        self.__check_status_code(res.status_code)

        result: str = res.text
        result: dict = json.loads(result)

        if result.get("status") == "theme not found":
            raise ValueError("THEME NOT FOUND")

        for _, info in result.items():
            vulnerabilities = info.get("vulnerabilities", [])

        return vulnerabilities

    def get_20_latest_vulnerable_themes(self) -> list[dict]:
        """Only available for premium users"""
        slug: str = "themes/latest"
        url: str = self.url + slug
        res = requests.get(url, headers=self.header)

        self.__check_status_code(res.status_code)

        result: str = res.text
        result: dict = json.loads(result)

        return result


class MissingTokenError(Exception):
    pass


class RateLimitExceededError(Exception):
    pass


class TooManyRequestsError(Exception):
    pass


class AuthenticationError(Exception):
    pass


if __name__ == "__main__":
    dotenv_path = Path("src/.env")
    load_dotenv(dotenv_path=dotenv_path)
    wps = WpsApi()
    print(wps.token)
    print(wps.requests_to_api_remaining)
    # sv = Saver("curse.local")
    # print(sv.folder_path)
    # print(wps.get_vulnerabilities_by_wp_version(643))
