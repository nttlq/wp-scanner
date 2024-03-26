import urllib3

from utils.printings import Printer
from utils.ags_parser import parser
from utils.file_manager import FileManager

from controllers.wp_site import WpSite
from controllers.brute_force import Bruteforce
from controllers.wps_api import WpsApi
from controllers.ports_scanner import PortScanner
from controllers.crawler import Crawler
from controllers.fuzzing import Fuzzing
from controllers.sql_injections import SQLInjectionScanner
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
    ports_scanner = PortScanner(wp_site)
    crawler = Crawler(wp_site)
    fuzzing = Fuzzing(wp_site)
    sqliscanner = SQLInjectionScanner(wp_site)
    file_manager = FileManager(wp_site)

    menu = Menu(
        wp_site,
        brute_force,
        wps_api,
        ports_scanner,
        crawler,
        fuzzing,
        sqliscanner,
        file_manager,
    )

    menu.check_is_wp()

    menu.parse_input()


def main():
    print(Printer.hello())
    start_application()
    print(Printer.author())


if __name__ == "__main__":
    main()
