import urllib3

from utils.printings import Printer
from utils.ags_parser import parser
from utils.file_manager import FileManager

from controllers.wp_site import WpSite
from controllers.brute_force import Bruteforce
from controllers.wps_api import WpsApi

from views.menu import Menu

##########################################


def start_application():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    args = parser()

    url = args.url[0]

    if type(args.user_agent) == list:
        user_agent = args.user_agent[0]
    else:
        user_agent = args.user_agent

    wp_site = WpSite(url, user_agent, args.https)
    bruteforce = Bruteforce(wp_site)
    wps_api = WpsApi()
    file_manager = FileManager(wp_site)
    print(wp_site.url)
    print(wp_site.user_agent)
    wp_site.detect_wp_version()
    print("WP version: ", wp_site.wp_version)
    wp_site.detect_themes()
    print("Themes: ", wp_site.themes)
    wp_site.detect_plugins()
    print("Plugins: ", wp_site.plugins)
    # print(Menu.options())

    logins = open("src/db/logins.txt", "r").read().split()
    passwords = open("src/db/passwords.txt", "r").read().split()
    # logins = ("user2",)
    # passwords = ("12345",)
    bruteforce.bruteforce(logins, passwords)
    print("Admin: ", bruteforce.admin)
    print("Logins: ", wp_site.logins)
    print("Users: ", wp_site.users)

    # t = input("promt: ")
    # print("T :", t)

    # wp_site.is_readme()


if __name__ == "__main__":
    Printer.print_all()
    # start_application()
