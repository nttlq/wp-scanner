import configparser
import random
import re
from typing import Generator

import requests

from utils.printings import Printer


class WpSite:
    __slots__ = (
        "__url",
        "__user_agent",
        "__http_ver",
        "__wp_version",
        "__users",
        "__themes",
        "__plugins",
        "__files",
        "__logins",
    )

    def __init__(self, url: str, user_agent: str = "rand", https: bool = False) -> None:
        self.__url: str = self.__check_url_integrity(url)
        self.__user_agent: str = self.__set_user_agent(user_agent)
        self.__http_ver: bool = https
        self.__wp_version: str = None
        self.__users: set[str] = set()
        self.__themes: dict[str, str] = {}
        self.__plugins: dict[str, str] = {}
        self.__files: set[str] = set()
        self.__logins: dict[str, str] = {}

        self.__check_is_wp()
        self.__check_is_installed()

    @property
    def users(self) -> set:
        return self.__users

    @property
    def themes(self) -> dict:
        return self.__themes

    @property
    def plugins(self) -> dict:
        return self.__plugins

    @property
    def files(self) -> set[str]:
        return self.__files

    def add_file(self, file: str):
        self.__files.add(file)

    @property
    def logins(self) -> dict:
        return self.__logins

    @property
    def wp_version(self) -> str:
        return self.__wp_version

    @property
    def url(self) -> str:
        complete_url = self.http_ver + self.__url + "/"
        return complete_url

    @Printer.info
    def print_user_agent(self) -> str:
        return self.__user_agent

    @property
    def user_agent(self) -> str:
        return self.__user_agent

    @property
    def http_ver(self) -> str:
        if self.__http_ver is True:
            return "https://"
        else:
            return "http://"

    def __check_url_integrity(self, url: str) -> str:

        url = url.lower()

        if url.startswith("http://"):
            url = url[7:]
            self.__http_ver = False
        elif url.startswith("https://"):
            url = url[8:]
            self.__http_ver = True

        valid_domains = (
            ".com",
            ".ru",
            ".local",
            ".ua",
            ".org",
            ".net",
            ".info",
            ".biz",
            ".gov",
            ".edu",
            ".mil",
            ".int",
            ".shop",
            ".store",
        )

        if not any(url.endswith(domain) for domain in valid_domains):
            raise ValueError(f"URL must end with {valid_domains}")

        return url

    def __set_user_agent(self, system: str = "rand") -> str:
        config = configparser.ConfigParser()
        config.read("src/db/user-agents.ini")

        if system == "rand":
            system = random.choice(["win", "mac", "linux", "ipad", "iphone"])

        random_user_agent = random.choice(config.options(system))

        user_agent = config.get(system, random_user_agent)

        return user_agent

    def __is_wp(self) -> bool:
        res = requests.get(
            self.url, headers={"User-Agent": self.__user_agent}, verify=False
        )
        if not "wp-" in res.text:
            return False
        else:
            return True

    def __check_is_wp(self) -> None:
        if self.__is_wp() is False:
            raise NameError(f"The site {self.url} is not on WordPress engine.")

    def __is_installed(self) -> bool:
        res = requests.get(
            self.url,
            allow_redirects=False,
            headers={"User-Agent": self.__user_agent},
            verify=False,
        )

        if "location" not in res.headers:
            return True

        header = str(res.headers["location"])
        slug = "wp-admin/setup-config.php"
        if slug in header:
            return False

        return True

    def __check_is_installed(self) -> None:
        if self.__is_installed() is False:
            print("The Website is currently in install mode.")

    def detect_users(self) -> bool:
        slug: tuple[str] = ("/?rest_route=/wp/v2/users", "/wp-json/wp/v2/users")

        res = requests.get(
            self.url + slug[0],
            headers={"User-Agent": self.user_agent},
            verify=False,
        )

        if res.status_code != 200:
            res = requests.get(
                self.url + slug[1],
                headers={"User-Agent": self.user_agent},
                verify=False,
            )

        users = res.json()
        if users == []:
            return False

        for user in users:
            self.__users.add(user["name"])  # FIXME: add a method

        return True

    def detect_robots_file(self) -> bool:
        slug: str = "robots.txt"
        res = requests.get(
            self.url + slug, headers={"User-Agent": self.__user_agent}, verify=False
        )

        if res.status_code == 200:
            self.add_file(slug)
            return True
        return False

        # lines = res.text.split('\n')
        # for l in lines:
        #     if "Disallow:" in l:
        #         print("\tInteresting entry from robots.txt: %s" % (l))

    def detect_readme_file(self) -> bool:
        slug = "readme.html"

        res = requests.get(
            self.url + slug,
            headers={"User-Agent": self.__user_agent},
            verify=False,
        )

        if res.status_code == 200:
            self.add_file(slug)

            return True

        return False
        # regular_expression = "Version (.*)"
        # regular_expression = re.compile(regular_expression)
        # matches = regular_expression.findall(res.text)

        # if len(matches) > 0 and matches[0] != None and matches[0] != "":
        #     self.version = matches[0]
        #     print(
        #         "The Wordpress '%s' file exposing a version number: %s"
        #         % (self.url + "readme.html", matches[0])
        #     )
        # else:
        #     print(
        #         "The Wordpress '%s' file is exposing a version number but it is not in the expected format"
        #         % (self.url + "readme.html")
        #     )

    def detect_wp_version(self) -> bool:
        slug: str = "index.php/feed"
        res = requests.get(
            self.url + slug,
            headers={"User-Agent": self.__user_agent},
            verify=False,
        )
        regular_expression = re.compile(
            r"generator>https://wordpress.org/\?v=(.*?)<\/generator"
        )
        found_matches = regular_expression.findall(res.text)

        if found_matches == []:
            return False

        self.__wp_version = found_matches[0]

        return True

    def detect_themes(self) -> bool:
        res = requests.get(
            self.url, headers={"User-Agent": self.__user_agent}, verify=False
        )

        slug: str = "wp-content/themes/"
        regular_expression = re.compile(rf"{slug}(.*?)/.*?[css|js].*?ver=([0-9\.]*)")
        found_matches = regular_expression.findall(res.text)
        themes: dict = {}

        if found_matches == []:
            return False

        for match in found_matches:
            themes[match[0]] = match[1]

        self.__themes = themes  # FIXME: add a method

        return True

    def detect_plugins(self) -> bool:
        res = requests.get(
            self.url, headers={"User-Agent": self.__user_agent}, verify=False
        )

        slug: str = "wp-content/plugins/"
        regular_expression = re.compile(rf"{slug}(.*?)/.*?[css|js].*?ver=([0-9\.]*)")
        found_matches = regular_expression.findall(res.text)
        plugins: dict = {}

        if found_matches == []:
            return False

        for match in found_matches:
            plugins[match[0]] = match[1]

        self.__plugins = plugins  # FIXME: add a method

        return True

    def check_themes(self, themes: tuple[str] = False) -> Generator[str, None, None]:
        if not themes:
            themes: tuple[str] = (
                "astra",
                "twentytwenty",
                "twentytwentytwo",
                "twentynineteen",
                "twentysixteen",
                "twentyseventeen",
                "twentyfifteen",
                "twentyfourteen",
                "twentythirteen",
                "twentytwelve",
                "twentyeleven",
                "twentyten",
            )
        slug: str = "wp-content/themes/"
        for theme in themes:
            res = requests.get(
                self.url + slug + theme,
                headers={"User-Agent": self.__user_agent},
                verify=False,
            )
            if res.status_code == 200:
                yield f"A default theme has been found in: {self.url + slug + theme}"
