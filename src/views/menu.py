import os
import sys
import re
from datetime import datetime

from colorama import Fore, Style

from utils.printings import Printer


class Menu:
    def __init__(
        self,
        wp_site,
        brute_force,
        wps_api,
        ports_scanner,
        crawler,
        fuzzing,
        sqliscanner,
        file_manager,
    ) -> None:
        self.wp_site = wp_site
        self.brute_force = brute_force
        self.wps_api = wps_api
        self.ports_scanner = ports_scanner
        self.crawler = crawler
        self.fuzzing = fuzzing
        self.sqliscanner = sqliscanner
        self.file_manager = file_manager

    @staticmethod
    @Printer.info
    def options() -> str:
        string = ""
        string += "OPTIONS" "\n"
        string += "[1] Basic Scan" "\n"
        string += "[2] Brute-force" "\n"
        string += "[3] Vulnerabilities Scan" "\n"
        string += "[4] Ports Scan" "\n"
        string += "[5] Crawler" "\n"
        string += "[6] Fuzzing" "\n"
        string += "[7] Show Report" "\n"
        string += "[8] Help" "\n"
        string += "[0] Exit"
        return string

    @staticmethod
    def clear() -> None:
        if "linux" in sys.platform:
            os.system("clear")
        elif "darwin" in sys.platform:
            os.system("clear")
        else:
            os.system("cls")

    def check_is_wp(self):
        option = input("Do you want to check if the site is a WordPress site? [0][1]: ")
        if option == "y" or option == "1" or option == "":
            self.wp_site.check_is_wp()
            self.wp_site.check_is_installed()
        elif option == "n" or option == "0":
            print(
                Fore.RED
                + "Warning! Most functions may not work correctly."
                + Style.RESET_ALL
            )
            pass

    def parse_input(self):
        while True:
            print(Menu.options())
            option = input("Choose an option: ")
            if option == "1":
                self.scan_all()
            elif option == "2":
                self.brute_forcing()
            elif option == "3":
                self.check_vulnerabilities()
            elif option == "4":
                self.check_ports()
            elif option == "5":
                self.crawl_website()
            elif option == "6":
                self.fuzzing_site()
            elif option == "7":
                self.show_report()
            elif option == "8":
                self.show_help()
            elif option == "exit" or option == "0":
                break
            elif option == "clear":
                Menu.clear()
            else:
                print("Invalid option")

    def show_help(self):
        print(
            Fore.GREEN
            + """
    [1] Basic Scan
    - Check if the site is a WordPress site
    - Check if WordPress is installed
    - Check WordPress version
    - Check users
    - Check usernames
    - Check themes
    - Check plugins
    - Check robots.txt
    - Check readme.html
    - Check directory listing
    - Check xml-rpc
    - Check debug.log
    - Check backups

    [2] Brute-force
    - Brute-force login page
    - Brute-force login page with custom logins and passwords
    - Brute-force login page with finded usernames

    [3] Vulnerabilities Scan
    - Check vulnerabilities for WordPress version
    - Check vulnerabilities for plugins
    - Check vulnerabilities for themes
    - Check vulnerabilities for SQL injections

    [4] Ports Scan
    - Scan ports
    - Scan ports in range

    [5] Crawler
    - Crawl website
    - Find injection urls
    - Find linked urls

    [6] Fuzzing
    - Fuzzing for themes
    - Fuzzing for plugins
    - Fuzzing for components

    [7] Show Report
    - Show report with all information

    [b][back] 
    - Back to main menu

    [clear] 
    - Clear the screen

    [0] Exit
    - Exit from the program
            """
            + Style.RESET_ALL
        )

    def is_valid_ports_input(self, ports):
        # Check if input is in the format "port-port"
        if re.match(r"^\d{1,5}-\d{1,5}$", ports):
            start_port, end_port = map(int, ports.split("-"))
            return 1 < start_port < 65535 and 1 < end_port < 65535

        # Check if input is in the format "port port ... port"
        if re.match(r"^(\d{1,5} )*\d{1,5}$", ports):
            return all(1 < int(port) < 65535 for port in ports.split())

        return False

    def check_ports(self):
        answ = input("Get IPs[0] or scan ports[1]?\n[0][1][b]: ")
        if answ == "0":
            self.ports_scanner.get_ips()
        elif answ == "1":
            if not self.wp_site.ips:
                print("Scan IPs first!")
                return
            ports = input("Choose an ports: ")
            if self.is_valid_ports_input(ports):
                if "-" in ports:
                    start_port, end_port = map(int, ports.split("-"))
                    self.scan_ports_in_range(start_port, end_port)
                else:
                    self.scan_ports(*map(int, ports.split()))
            else:
                print(
                    "Invalid input. Please enter ports in the format 'port-port' or 'port port ... port'."
                )
        elif answ == "b" or answ == "back":
            return

    def fuzzing_site(self):
        answ = input(
            "Fuzzing for themes[0] or plugins[1] or components[2]?\n[0][1][2][b]: "
        )
        if answ == "0":
            self.fuzzing.fuzzing_themes()
        elif answ == "1":
            self.fuzzing.fuzzing_plugins()
        elif answ == "2":
            self.fuzzing.fuzzing_components()
        elif answ == "b" or answ == "back":
            return
        else:
            print("Invalid option")

    def scan_ports_in_range(self, start_port, end_port):
        self.ports_scanner.scan_ports_in_range(start_port, end_port)

    def crawl_website(self):
        answ = input("Crawl site for linked urls[0] or injection urls[1]?\n[0][1][b]: ")
        if answ == "0":
            max_depth = int(input("Enter max depth: "))
            self.crawler.crawl_website(max_depth)
        elif answ == "1":
            answ = input("Main url only?\n[0][1][b]: ")
            if answ == "1":
                self.crawler.find_injection_urls(main_url_only=True)
            elif answ == "0":
                self.crawler.find_injection_urls()
            elif answ == "b" or answ == "back":
                return
        elif answ == "b" or answ == "back":
            return

    def scan_ports(self, *ports):
        port_list = list(ports)
        self.ports_scanner.scan_ports(*port_list)

    def check_sqli_vulnerabilities(self):
        if self.wp_site.injection_urls:
            answ = input("Use custom payloads[1] or default[0]?\n[0][1][b]: ")
            if answ == "1":
                answ = input("Enter the path to the file with payloads: ")
                self.sqliscanner.detect_sqli_vulnerability(answ)
            elif answ == "0":
                self.sqliscanner.detect_sqli_vulnerability()
            elif answ == "b" or answ == "back":
                return
        else:
            print("Scan site for sqli urls first!")

    def check_vulnerabilities(self):
        answ = input(
            "Check vulnerabilities for wp[0] or sql injections[1]?\n[0][1][b]: "
        )
        if answ == "0":
            answ = input(
                "Check vulnerabilities for wp version[0], plugins[1] or themes[2]?\nCheck requests to api remaining[3]\n[0][1][2][3][b]: "
            )
            if answ == "0":
                print("Getting vulnerabilities by WP version...")
                wp_version_str = list(self.wp_site.wp_version.keys())[0]
                wp_version_int = int(wp_version_str.replace(".", ""))
                vulnerabilities = self.wps_api.get_vulnerabilities_by_wp_version(
                    wp_version_int
                )
                if vulnerabilities:
                    self.wp_site.wp_version[wp_version_str] = vulnerabilities
                else:
                    self.wp_site.wp_version[wp_version_str] = "No vulnerabilities found"
            elif answ == "1":
                print("Getting vulnerabilities by plugin...")
                plugins = self.wp_site.plugins.keys()
                for plugin in plugins:
                    vulnerabilities = self.wps_api.get_vulnerabilities_by_plugin(plugin)
                    if vulnerabilities:
                        self.wp_site.plugins[plugin] = vulnerabilities
                    else:
                        self.wp_site.plugins[plugin] = "No vulnerabilities found"
            elif answ == "2":
                print("Getting vulnerabilities by theme...")
                themes = self.wp_site.themes.keys()
                for theme in themes:
                    vulnerabilities = self.wps_api.get_vulnerabilities_by_theme(theme)
                    if vulnerabilities:
                        self.wp_site.themes[theme] = vulnerabilities
                    else:
                        self.wp_site.themes[theme] = "No vulnerabilities found"
            elif answ == "3":
                res = self.wps_api.get_requests_to_api_remaining_of_all_tokens()
                print("Requests remaining: ", res)
            elif answ == "b" or answ == "back":
                return
        elif answ == "1":
            self.check_sqli_vulnerabilities()
        elif answ == "b" or answ == "back":
            return

    def scan_all(self):
        self.wp_site.detect_wp_version()
        self.wp_site.detect_users()
        self.wp_site.detect_usernames()
        self.wp_site.detect_themes()
        self.wp_site.detect_plugins()
        self.wp_site.detect_robots_file()
        self.wp_site.detect_readme_file()
        self.wp_site.is_directory_listing()
        self.wp_site.detect_xml_rpc()
        self.wp_site.is_debug_log()
        self.wp_site.detect_backups()

    def brute_forcing(self):
        answ = input(
            "Enter the custom database for logins and passwords[1] or Default[0]\n[0][1][b]: "
        )
        if answ == "0":
            answ = input("Usernames finded from site[1] or predefined[0]?\n[0][1][b]: ")
            if answ == "1":
                if self.wp_site.usernames:
                    logins = self.wp_site.usernames
                    print("Logins: ", logins)
                else:
                    print("Scan users in first!")
                    return
            elif answ == "0":
                logins = open("src/db/logins.txt", "r").read().split()
            elif answ == "b" or answ == "back":
                return

            passwords = open("src/db/passwords.txt", "r").read().split()

        elif answ == "1":
            path_logins = input("Enter the path to the file with logins: ")
            path_passwords = input("Enter the path to the file with passwords: ")
            try:
                logins = open(path_logins, "r").read().split()
                passwords = open(path_passwords, "r").read().split()
            except FileNotFoundError as e:
                print("File not found: ", e)
                return
        elif answ == "b" or answ == "back":
            return

        self.brute_force.bruteforce(logins, passwords)

    def save_report(self):
        file_content = ""
        file_content += "[Report]" + "\n"
        file_content += (
            "URL: "
            + (str(self.wp_site.url) if self.wp_site.url else "Not found")
            + "\n"
        )
        file_content += (
            "User-Agent: "
            + (str(self.wp_site.user_agent) if self.wp_site.user_agent else "Not found")
            + "\n"
        )
        file_content += (
            "WP version: "
            + (str(self.wp_site.wp_version) if self.wp_site.wp_version else "Not found")
            + "\n"
        )
        file_content += (
            "Themes: "
            + (str(self.wp_site.themes) if self.wp_site.themes else "Not found")
            + "\n"
        )
        file_content += (
            "Plugins: "
            + (str(self.wp_site.plugins) if self.wp_site.plugins else "Not found")
            + "\n"
        )
        file_content += (
            "Logins: "
            + (str(self.wp_site.logins) if self.wp_site.logins else "Not found")
            + "\n"
        )
        file_content += (
            "Users: "
            + (str(self.wp_site.users) if self.wp_site.users else "Not found")
            + "\n"
        )
        file_content += (
            "Files: "
            + (str(self.wp_site.files) if self.wp_site.files else "Not found")
            + "\n"
        )
        file_content += (
            "Usernames: "
            + (str(self.wp_site.usernames) if self.wp_site.usernames else "Not found")
            + "\n"
        )
        file_content += (
            "Admin: "
            + (str(self.wp_site.admin) if self.wp_site.admin else "Not found")
            + "\n"
        )
        file_content += (
            "Ips: "
            + (str(self.wp_site.ips) if self.wp_site.ips else "Not found")
            + "\n"
        )
        file_content += (
            "Ports: "
            + (str(self.wp_site.ports) if self.wp_site.ports else "Not found")
            + "\n"
        )
        file_content += (
            "All Forms: "
            + (str(self.wp_site.all_forms) if self.wp_site.all_forms else "Not found")
            + "\n"
        )
        file_content += (
            "Linked urls: "
            + (
                str(self.wp_site.linked_urls)
                if self.wp_site.linked_urls
                else "Not found"
            )
            + "\n"
        )
        file_content += (
            "Injection urls: "
            + (
                str(self.wp_site.injection_urls)
                if self.wp_site.injection_urls
                else "Not Found"
            )
            + "\n"
        )
        file_content += (
            "Sqli vulnerable urls: "
            + (
                str(self.wp_site.sqli_vulnerable_urls)
                if self.wp_site.sqli_vulnerable_urls
                else "Not found"
            )
            + "\n"
        )
        now = datetime.now()
        filename = "report_" + now.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"

        self.file_manager.save_file(filename, file_content)

    def show_report(self):
        print(Fore.LIGHTGREEN_EX + "[Report]" + Style.RESET_ALL)
        print("URL: ", self.wp_site.url)
        print("User-Agent: ", self.wp_site.user_agent)
        print(
            "WP version: ",
            (
                self.wp_site.wp_version
                if self.wp_site.wp_version
                else Fore.RED + "Not found" + Style.RESET_ALL
            ),
        )
        print(
            "Themes: ",
            (
                self.wp_site.themes
                if self.wp_site.themes
                else Fore.RED + "Not found" + Style.RESET_ALL
            ),
        )
        print(
            "Plugins: ",
            (
                self.wp_site.plugins
                if self.wp_site.plugins
                else Fore.RED + "Not found" + Style.RESET_ALL
            ),
        )
        print(
            "Logins: ",
            (
                self.wp_site.logins
                if self.wp_site.logins
                else Fore.RED + "Not found" + Style.RESET_ALL
            ),
        )
        print(
            "Users: ",
            (
                self.wp_site.users
                if self.wp_site.users
                else Fore.RED + "Not found" + Style.RESET_ALL
            ),
        )
        print(
            "Files: ",
            (
                self.wp_site.files
                if self.wp_site.files
                else Fore.RED + "Not found" + Style.RESET_ALL
            ),
        )
        print(
            "Usernames: ",
            (
                self.wp_site.usernames
                if self.wp_site.usernames
                else Fore.RED + "Not found" + Style.RESET_ALL
            ),
        )
        print(
            "Admin: ",
            (
                self.wp_site.admin
                if self.wp_site.admin
                else Fore.RED + "Not found" + Style.RESET_ALL
            ),
        )
        print(
            "Ips: ",
            (
                self.wp_site.ips
                if self.wp_site.ips
                else Fore.RED + "Not found" + Style.RESET_ALL
            ),
        )
        print(
            "Ports: ",
            (
                self.wp_site.ports
                if self.wp_site.ports
                else Fore.RED + "Not found" + Style.RESET_ALL
            ),
        )
        print(
            "All Forms: ",
            (
                self.wp_site.all_forms
                if self.wp_site.all_forms
                else Fore.RED + "Not found" + Style.RESET_ALL
            ),
        )
        print(
            "Linked urls: ",
            (
                self.wp_site.linked_urls
                if self.wp_site.linked_urls
                else Fore.RED + "Not found" + Style.RESET_ALL
            ),
        )
        print(
            "Injection urls: ",
            (
                self.wp_site.injection_urls
                if self.wp_site.injection_urls
                else Fore.RED + "Not found" + Style.RESET_ALL
            ),
        )
        print(
            "Sqli vulnerable urls: ",
            (
                self.wp_site.sqli_vulnerable_urls
                if self.wp_site.sqli_vulnerable_urls
                else Fore.RED + "Not found" + Style.RESET_ALL
            ),
        )

        self.save_report()
