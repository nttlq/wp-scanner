from pathlib import Path

import urllib3
from dotenv import load_dotenv

from utils.printings import Printer
from utils.ags_parser import parser
from utils.file_manager import FileManager

from controllers.wp_site import WpSite
from controllers.brute_force import Bruteforce
from controllers.wps_api import WpsApi

from views.menu import Menu


def start_application():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    args = parser()

    url = args.url[0]

    if type(args.user_agent) == list:
        user_agent = args.user_agent[0]
    else:
        user_agent = args.user_agent

    wp_site = WpSite(url, user_agent, args.https)
    brute_force = Bruteforce(wp_site)
    wps_api = WpsApi()
    file_manager = FileManager(wp_site)
    menu = Menu(wp_site, brute_force, wps_api)

    menu.parse_input()


# TODO: scanner portov
def main():
    dotenv_path = Path("src/.env")
    load_dotenv(dotenv_path=dotenv_path)
    print(Printer.hello())
    start_application()
    print(Printer.author())


if __name__ == "__main__":
    main()
