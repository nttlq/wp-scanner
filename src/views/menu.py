import re
from utils.printings import Printer


def is_valid_ports_input(ports):
    # Check if input is in the format "port-port"
    if re.match(r"^\d{1,5}-\d{1,5}$", ports):
        start_port, end_port = map(int, ports.split("-"))
        return 1 < start_port < 65535 and 1 < end_port < 65535

    # Check if input is in the format "port port ... port"
    if re.match(r"^(\d{1,5} )*\d{1,5}$", ports):
        return all(1 < int(port) < 65535 for port in ports.split())

    # If input doesn't match any of the expected formats, it's invalid
    return False


class Menu:
    def __init__(
        self, wp_site, brute_force, wps_api, ports_scanner, file_manager
    ) -> None:
        self.wp_site = wp_site
        self.brute_force = brute_force
        self.wps_api = wps_api
        self.ports_scanner = ports_scanner
        self.file_manager = file_manager

    @staticmethod
    @Printer.info
    def options() -> str:
        string = ""
        string += "OPTIONS" + "\n"
        string += "[1] Scan" "\n"
        string += "[2] Brutforce" "\n"
        string += "[3] Check vulnerabilities" "\n"
        string += "[4] Scan ports" "\n"
        string += "[5] Show Report" "\n"
        string += "[exit]"
        return string

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
                ports = input("Choose an ports: ")

                if is_valid_ports_input(ports):
                    if "-" in ports:
                        start_port, end_port = map(int, ports.split("-"))
                        self.scan_ports_in_range(start_port, end_port)
                    else:
                        self.scan_ports(*map(int, ports.split()))
                else:
                    print(
                        "Invalid input. Please enter ports in the format 'port-port' or 'port port ... port'."
                    )

                # self.scan_ports(ports)
            elif option == "5":
                self.show_report()
            elif option == "exit" or option == "0":
                break
            else:
                print("Invalid option")

    def scan_ports_in_range(self, start_port, end_port):
        self.ports_scanner.scan_ports_in_range(start_port, end_port)

    def scan_ports(self, *ports):
        port_list = list(ports)
        print("PORTS: ", type(port_list))
        self.ports_scanner.scan_ports(*port_list)

    def scan_ports2(self, ports):
        port_list = [int(p) for p in ports.split(" ")]
        print("PORTS: ", type(port_list))
        self.ports_scanner.scan_ports(*port_list)

    def check_vulnerabilities(self):
        # self.wps_api.get_vulnerabilities_by_wp_version(self.wp_site.wp_version)
        plugins = self.wp_site.plugins.keys()
        for plugin in plugins:
            vulnerabilities = self.wps_api.get_vulnerabilities_by_plugin(plugin)
            self.wp_site.plugins[plugin] = vulnerabilities
        themes = self.wp_site.themes.keys()
        for theme in themes:
            vulnerabilities = self.wps_api.get_vulnerabilities_by_theme(theme)

            self.wp_site.themes[theme] = vulnerabilities

    def scan_all(self):
        self.wp_site.detect_wp_version()
        self.wp_site.detect_users()
        self.wp_site.detect_themes()
        self.wp_site.detect_plugins()
        self.wp_site.detect_robots_file()
        self.wp_site.detect_readme_file()

    def brute_forcing(self):
        logins = open("src/db/logins.txt", "r").read().split()
        passwords = open("src/db/passwords.txt", "r").read().split()
        # logins = ("user2",)
        # passwords = ("12345",)
        self.brute_force.bruteforce(logins, passwords)

    def save_report(self):
        file_content = ""
        file_content += "Report" + "\n"
        file_content += "URL: " + str(self.wp_site.url) + "\n"
        file_content += "User-Agent: " + str(self.wp_site.user_agent) + "\n"
        file_content += "WP version: " + str(self.wp_site.wp_version) + "\n"
        file_content += "Themes: " + str(self.wp_site.themes) + "\n"
        file_content += "Plugins: " + str(self.wp_site.plugins) + "\n"
        file_content += "Logins: " + str(self.wp_site.logins) + "\n"
        file_content += "Users: " + str(self.wp_site.users) + "\n"
        file_content += "Files: " + str(self.wp_site.files) + "\n"
        file_content += "Usernames: " + str(self.wp_site.usernames) + "\n"
        file_content += "Admin: " + str(self.wp_site.admin) + "\n"
        file_content += "Ips: " + str(self.wp_site.ips) + "\n"
        file_content += "Ports: " + str(self.wp_site.ports) + "\n"
        # file_content += "Is Installed: " + str(self.wp_site.is_installed) + "\n"
        # file_content += "Is WP: " + str(self.wp_site.is_wp) + "\n"
        # file_content += "Is HTTPS: " + str(self.wp_site.http_ver) + "\n"
        # file_content += (
        #     "Requests to API remaining: "
        #     + str(self.wps_api.requests_to_api_remaining)
        #     + "\n"
        # )
        # file_content += "Is Robots: " + str(self.wp_site.is_robots) + "\n"
        self.file_manager.save_file("report.txt", file_content)

    def show_report(self):
        print("Report")
        print("URL: ", self.wp_site.url)
        print("User-Agent: ", self.wp_site.user_agent)
        print("WP version: ", self.wp_site.wp_version)
        print("Themes: ", self.wp_site.themes)
        print("Plugins: ", self.wp_site.plugins)
        print("Logins: ", self.wp_site.logins)
        print("Users: ", self.wp_site.users)
        print("Files: ", self.wp_site.files)
        print("Usernames: ", self.wp_site.usernames)
        print("Admin: ", self.wp_site.admin)
        print("Ips: ", self.wp_site.ips)
        print("Ports: ", self.wp_site.ports)
        # print("Is Readme: ", self.wp_site.is_readme)
        # print("Is Installed: ", self.wp_site.is_installed)
        # print("Is WP: ", self.wp_site.is_wp)
        print("Is HTTPS: ", self.wp_site.http_ver)
        # print("Requests to API remaining: ", self.wps_api.requests_to_api_remaining)
        self.save_report()
        # print("Is Robots: ", self.wp_site.is_robots)
        # print("Is Sitemap: ", self.wp_site.is_sitemap)
        # print("Is Favicon: ", self.wp_site.is_favicon)
        # print("Is Login: ", self.wp_site.is_login)
        # print("Is Admin: ", self.wp_site.is_admin)
        # print("Is XMLRPC: ", self.wp_site.is_xmlrpc)
