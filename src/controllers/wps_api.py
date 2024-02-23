import os
import json

import requests


class WpsApi:
    __slots__ = (
        "__url",
        "__header",
        "__tokens",
        "__token",
    )

    def __init__(self):
        self.__url: str = "https://wpscan.com/api/v3/"
        self.__header: dict[str, str] = {}
        self.__tokens: list[str] = self.__read_tokens()
        self.__token: str = self.__set_token()

        # self.__header = self.__set_header()
        # self.__requests_to_api_remaining = self.__get_requests_to_api_remaining()

        # self.__check_requests_to_api_remaining()

    @property
    def header(self) -> dict[str, str]:
        return self.__header

    @property
    def url(self) -> str:
        return self.__url

    @property
    def token(self) -> str:
        return self.__token

    def __read_tokens(self) -> list[str]:
        tokens = []
        with open("src/db/tokens_api.txt", "r") as file:
            tokens = file.read().split()
        print("Tokens: ", *tokens)
        return tokens

    def __set_header(self, token: str) -> dict[str, str]:
        header = {"Authorization": f"Token token={token}"}

        return header

    def __set_token(self) -> str:
        if not self.__tokens:
            raise MissingTokenError("NO TOKENS AVAILABLE")

        for token in self.__tokens:
            if len(token) != 43:
                raise ValueError("INVALID TOKEN")

            self.__header = self.__set_header(token)
            print("Token: ", token)
            if self.__check_requests_to_api_remaining():
                return token

        raise RateLimitExceededError("NO REQUESTS REMAINING")

    # @property
    # def requests_to_api_remaining(self) -> int:
    #     return self.__requests_to_api_remaining

    def __check_requests_to_api_remaining(self) -> bool:
        if self.__get_requests_to_api_remaining() <= 0:
            return False
        return True

    def __get_requests_to_api_remaining(self) -> int:
        slug: str = "status"
        get_status_url: str = self.url + slug
        res = requests.get(get_status_url, headers=self.header)

        self.__check_status_code(res.status_code)

        result: str = res.text
        result: dict = json.loads(result)
        result: int = result.get("requests_remaining")
        print("Requests remaining: ", result)

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
            return None
            # raise ValueError("PLUGIN NOT FOUND")

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
            return None
            # raise ValueError("THEME NOT FOUND")

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
    from dotenv import load_dotenv
    from pathlib import Path

    dotenv_path = Path("src/.env")
    load_dotenv(dotenv_path=dotenv_path)
    wps = WpsApi()
    print(wps.token)
    print(wps.requests_to_api_remaining)
    # sv = Saver("curse.local")
    # print(sv.folder_path)
    theme = "wpengine-magazine"
    plugin = "wpengine-tag-manager"
    print(wps.get_vulnerabilities_by_plugin(plugin))
