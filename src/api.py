"""
{
    "name": "moxorew540@rohoza.com",
    "email": "moxorew540@rohoza.com",
    "password": "moxorew540@rohoza.com",
    "password_confirmation": "moxorew540@rohoza.com",
    "homepage": "",
    "twitter": "",
    "address_line1": "",
    "address_line2": "",
    "address_city": "",
    "address_postal_code": "",
    "address_state": "",
    "address_country": "",
    "tax_id_data_type": "",
    "tax_id_data_value": "",
    "monthly_digest": false,
    "newsletter": false,
    "terms_accepted": true
}

# POST 
https://wpscan.com/wp-json/wpscan/v1/sign-up

GET
https://wpscan.com/confirm?token=PpL0dtjeY2nyEu3tcO5i

# POST
https://wpscan.com/wp-json/wpscan/v1/sign-in

{
    "email": "moxorew540@rohoza.com",
    "password": "moxorew540@rohoza.com",
    "remember_me": false
}

GET
https://wpscan.com/profile/

"""

import os
import json
from pathlib import Path

from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import urllib3


class WPS_API:
    def __init__(self):
        self.__token: str = self.__get_token()
        self.__url: str = "https://wpscan.com/api/v3/"
        self.__header = self.__set_header()
        self.__req_remaining = self.__get_req_remaining()
        self.__check_req_remaining()

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

    def __get_token(self) -> str:
        token: str = os.environ.get("WPS_API_TOKEN")
        if not token:
            raise MissingTokenError("TOKEN NOT FOUND")

        return token

    @property
    def req_remaining(self) -> int:
        return self.__req_remaining

    def __check_req_remaining(self) -> bool:
        if self.req_remaining <= 0:
            raise RateLimitExceededError("NO REQUESTS REMAINING")
        return True

    def __get_req_remaining(self) -> int:
        slug: str = "status"
        get_status_url: str = self.url + slug
        response = requests.get(get_status_url, headers=self.header)

        if response.status_code != 200:
            raise AuthenticationError("TOKEN EXPIRED OR INVALID")

        result: str = response.text
        result: dict = json.loads(result)
        result: int = result.get("requests_remaining")

        return result

    def get_vulnerabilities_by_wp_version(self, version: int) -> dict:
        slug: str = f"wordpresses/{version}"
        get_vulnerabilities_url: str = self.url + slug
        response = requests.get(get_vulnerabilities_url, headers=self.header)

        if response.status_code != 200:
            raise TooManyRequestsError("TOO MANY REQUESTS")

        result: str = response.text
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
    wps = WPS_API()
    print(wps.token)
    print(wps.req_remaining)


def test():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = {
        "Authorization": "Token token=sST2gat5Bnsv9mGnUjD4zugVhRMByqmBt6eYOaOXMxc"
    }
    vulnerabilities_url = "https://wpscan.com/api/v3/status"
    # x='1-flash-gallery'
    respons = requests.get(vulnerabilities_url, headers=headers)
    print(respons.status_code)
    print(respons.text)
    with requests.Session() as s:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5"
        }
        datas = {
            "email": "moxorew540@rohoza.com",
            "password": "moxorew540@rohoza.com",
            "remember_me": "false",
        }
        login = "https://wpscan.com/wp-json/wpscan/v1/sign-in"
        res0 = s.post(login, headers=headers, data=datas)
        # print(res0.text)
        print(res0.status_code)
        # temp_soup = BeautifulSoup(res.text, "html.parser")

        res = s.get("https://wpscan.com/profile/")
        soup = BeautifulSoup(res.text, "html.parser")
        print(res.status_code)
        # Find the element with class 'K6cz826AYNjox0qiXyFv'
        element = soup.find(class_="K6cz826AYNjox0qiXyFv")

        # Read the text from the <p> tag within the class
        if element:
            p_text = element.find("p").text
            print(p_text)
