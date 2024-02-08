import argparse
import configparser
import random
import re
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
import urllib3

from printings import Printer


@dataclass()
class User:
    name: str


@dataclass()
class Site:
    url: str
    user_agent: str
    https: bool


class Scanner:
    def __init__(self, url: str, user_agent: str = "rand", https: bool = False) -> None:
        self.__url: str = self.__check_url_integrity(url)
        self.__user_agent: str = self.__set_user_agent(user_agent)
        self.__http_ver: bool = https
        self.__version = None
        self.users = set()
        if self.__is_wp() is False:
            raise NameError(f"The site {self.url} is not on WordPress engine.")
        if self.__is_installed() is False:
            print(
                "The Website is not fully configured and currently in install mode. Call it to create a new admin user."
            )

    @property
    def version(self) -> str:
        return self.__version

    @version.setter
    def version(self, version: str) -> None:
        self.__version = version

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

    def __check_url_integrity(self, url):

        url = url.lower()

        if url.startswith("http://"):
            url = url[7:]
            self.__http_ver = False
        elif url.startswith("https://"):
            url = url[8:]
            self.__http_ver = True

        valid_domains = (".com", ".ru", ".local")
        if not any(url.endswith(domain) for domain in valid_domains):
            raise ValueError(f"URL must end with {valid_domains}")

        return url

    def __set_user_agent(self, system: str):
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

    def is_readme(self):
        r = requests.get(
            self.url + "readme.html",
            headers={"User-Agent": self.__user_agent},
            verify=False,
        )

        if "200" in str(r):
            # self.files.add("readme.html")

            # Basic version fingerprinting
            regex = "Version (.*)"
            regex = re.compile(regex)
            matches = regex.findall(r.text)

            if len(matches) > 0 and matches[0] != None and matches[0] != "":
                self.version = matches[0]
                print(
                    "The Wordpress '%s' file exposing a version number: %s"
                    % (self.url + "readme.html", matches[0])
                )
            else:
                print(
                    "The Wordpress '%s' file is exposing a version number but it is not in the expected format"
                    % (self.url + "readme.html")
                )
            # print(r.text)

    def __is_installed(self):
        try:
            res = requests.get(
                self.url,
                allow_redirects=False,
                headers={"User-Agent": self.__user_agent},
                verify=False,
            )

            if "location" not in res.headers:
                return True
            header = str(res.headers["location"])
            # print(header)

            if "wp-admin/setup-config.php" in header:
                return False
                #    "The Website is not fully configured and currently in install mode. Call it to create a new admin user."

        except Exception as e:
            print(e)
            exit()

    def is_backup_file(self):
        backup = [
            "wp-config.php~",
            "wp-config.php.save",
            ".wp-config.php.bck",
            "wp-config.php.bck",
            ".wp-config.php.swp",
            "wp-config.php.swp",
            "wp-config.php.swo",
            "wp-config.php_bak",
            "wp-config.bak",
            "wp-config.php.bak",
            "wp-config.save",
            "wp-config.old",
            "wp-config.php.old",
            "wp-config.php.orig",
            "wp-config.orig",
            "wp-config.php.original",
            "wp-config.original",
            "wp-config.txt",
            "wp-config.php.txt",
            "wp-config.backup",
            "wp-config.php.backup",
            "wp-config.copy",
            "wp-config.php.copy",
            "wp-config.tmp",
            "wp-config.php.tmp",
            "wp-config.zip",
            "wp-config.php.zip",
            "wp-config.db",
            "wp-config.php.db",
            "wp-config.dat",
            "wp-config.php.dat",
            "wp-config.tar.gz",
            "wp-config.php.tar.gz",
            "wp-config.back",
            "wp-config.php.back",
            "wp-config.test",
            "wp-config.php.test",
            "wp-config.php.1",
            "wp-config.php.2",
            "wp-config.php.3",
            "wp-config.php._inc",
            "wp-config_inc",
            "wp-config.php.SAVE",
            ".wp-config.php.BCK",
            "wp-config.php.BCK",
            ".wp-config.php.SWP",
            "wp-config.php.SWP",
            "wp-config.php.SWO",
            "wp-config.php_BAK",
            "wp-config.BAK",
            "wp-config.php.BAK",
            "wp-config.SAVE",
            "wp-config.OLD",
            "wp-config.php.OLD",
            "wp-config.php.ORIG",
            "wp-config.ORIG",
            "wp-config.php.ORIGINAL",
            "wp-config.ORIGINAL",
            "wp-config.TXT",
            "wp-config.php.TXT",
            "wp-config.BACKUP",
            "wp-config.php.BACKUP",
            "wp-config.COPY",
            "wp-config.php.COPY",
            "wp-config.TMP",
            "wp-config.php.TMP",
            "wp-config.ZIP",
            "wp-config.php.ZIP",
            "wp-config.DB",
            "wp-config.php.DB",
            "wp-config.DAT",
            "wp-config.php.DAT",
            "wp-config.TAR.GZ",
            "wp-config.php.TAR.GZ",
            "wp-config.BACK",
            "wp-config.php.BACK",
            "wp-config.TEST",
            "wp-config.php.TEST",
            "wp-config.php._INC",
            "wp-config_INC",
        ]

        for b in backup:
            r = requests.get(
                self.url + b, headers={"User-Agent": self.__user_agent}, verify=False
            )
            if "200" in str(r) and not "404" in r.text:
                # self.files.add(b)
                print(
                    "A wp-config.php backup file has been found in: %s" % (self.url + b)
                )

    def fingerprint_wp_version_feed_based(self):
        r = requests.get(
            self.url + "index.php/feed",
            headers={"User-Agent": self.__user_agent},
            verify=False,
        ).text
        regex = re.compile("generator>https://wordpress.org/\?v=(.*?)<\/generator")
        match = regex.findall(r)
        if match != []:
            self.version = match[0]
            print(
                "WordPress version %s identified from advanced fingerprinting"
                % self.version
            )
            return True
        return False


def test():
    # Read user agents from the ini file
    config = configparser.ConfigParser()
    config.read("src/db/user-agents.ini")

    user_agent2 = random.choice(config.options("Mac"))
    user_agent = config.get("Windows", user_agent2)
    # user_agents = config["Windows"]
    print(user_agent)
    print("UA2: ", user_agent2)
    print("Type: ", type(user_agent))
    # Select a random user agent
    # user_agent_list = user_agent.split("\n")
    # random_user_agent = random.choice(user_agent_list)

    # print(random_user_agent)

    wp_login = "http://curse.local/wp-login.php"
    wp_admin = "http://curse.local/wp-admin/"
    username = "admin"
    password = "admin"

    with requests.Session() as s:
        headers1 = {f"User-Agent: {user_agent}"}
        # print(headers1)
        datas = {
            "log": username,
            "pwd": password,
            "wp-submit": "Log In",
            "redirect_to": wp_admin,
        }
        res = s.post(wp_login, json=headers1, data=datas, verify=False)
        temp_soup = BeautifulSoup(res.text, "html.parser")
        # print(temp_soup.text)
        print(res.status_code)
        # print(res.headers)


# args.user_agent = random_user_agent

# Use the selected user agent for scanning the site
# Your code for scanning the site goes here


def parser():
    parser = argparse.ArgumentParser(description="Process of scanning a wp site.")
    parser.add_argument(
        "url",
        metavar="URL",
        type=str,
        nargs=1,
        help="The URL of the site to scan.",
    )

    user_agents = ("rand", "win", "mac", "linux", "ipad", "iphone")
    parser.add_argument(
        "--user_agent",
        "-u",
        dest="user_agent",
        type=str,
        choices=user_agents,
        default=user_agents[0],
        nargs=1,
        help="The user agent to use when scanning the site.",
    )

    parser.add_argument(
        "--https",
        "-s",
        action="store_true",
        dest="https",
        default=False,
        help="Use https when scanning the site.",
    )

    args = parser.parse_args()
    return args


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    args = parser()

    url = args.url[0]

    if type(args.user_agent) == list:
        user_agent = args.user_agent[0]
    else:
        user_agent = args.user_agent

    sc = Scanner(url, user_agent, args.https)
    print(sc.url)
    print(sc.user_agent)
    sc.fingerprint_wp_version_feed_based()
    print(Menu.options())

    t = input("promt: ")
    print("T :", t)
    # sc.is_readme()
    # sc.is_up_and_installed()
    # is_wordpress(url=protocol + url, agent=user_agent, nocheck=False)


def database_update():
    print("\033[93mUpdating database\033[92m - Last update: \033[0m")
    update_url = "https://data.wpscan.org/"
    update_files = [
        "local_vulnerable_files.xml",
        "local_vulnerable_files.xsd",
        "timthumbs.txt",
        "user-agents.txt",
        "wp_versions.xml",
        "wp_versions.xsd",
        "wordpresses.json",
        "plugins.json",
        "themes.json",
    ]

    for f in update_files:
        print("\t\033[93mDownloading \033[0m" + f + " \033[92mFile updated !\033[0m")
        download_file(update_url + f, "database/" + f, True)

    unzip_file("database/user-agents.txt")
    unzip_file("database/timthumbs.txt")


def download_raw_file(url, filename, verbosity):
    try:

        # Open the request
        source = requests.get(url, stream=True).raw

        # Write the file
        with open(filename, "wb+") as ddl_file:
            progress = 0
            while True:
                length = 16 * 1024
                buf = source.read(length)
                if not buf:
                    break
                ddl_file.write(buf)
                progress += len(buf)

                if verbosity == True:
                    print(
                        "\tDownloaded : %.2f Mo\r" % (float(progress) / (1024 * 1024))
                    ),

    except Exception as e:
        raise e


def download_file(url, filename, verbosity):
    try:

        # Open the request
        source = requests.get(url).text

        # Write the file
        with open(filename, "wb") as ddl_file:
            ddl_file.write(source.encode("utf8"))

    except Exception as e:
        raise e


import os


def unzip_file(filename):
    with open(filename, "r") as f:
        data = f.read()

    # Check for a buggy .gz
    if not "/timthumb.php" in data and not "Mozilla/5.0" in data:
        os.system("mv " + filename + " " + filename + ".gz")
        os.system("gzip -d " + filename + ".gz")


class Menu:
    @staticmethod
    @Printer.info
    def options() -> str:
        string = ""
        string += "OPTIONS" + "\n"
        string += "[1] Brutforce" "\n"
        string += "[2] Change User-Agent" "\n"
        string += "[3] Show Stats" "\n"
        return string


if __name__ == "__main__":
    # database_update()
    Printer.print_all()
    main()
