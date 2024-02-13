from utils.printings import Printer


class Menu:
    def __init__(self, wp_site, brute_force, wps_api) -> None:
        self.wp_site = wp_site
        self.brut_force = brute_force
        self.wps_api = wps_api

    @staticmethod
    @Printer.info
    def options() -> str:
        string = ""
        string += "OPTIONS" + "\n"
        string += "[1] Scan" "\n"
        string += "[2] Brutforce" "\n"
        string += "[3] Check vulnerabilities" "\n"
        string += "[4] Show Report" "\n"
        string += "[exit]"
        return string

    def parse_input(self):
        while True:
            print(Menu.options())
            option = input("Choose an option: ")
            if option == "1":
                self.scan_all()
            elif option == "2":
                self.brute_force()
            elif option == "3":
                self.check_vulnerabilities()
            elif option == "4":
                self.show_report()
            elif option == "exit":
                break
            else:
                print("Invalid option")

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

    def brute_force(self):
        logins = open("src/db/logins.txt", "r").read().split()
        passwords = open("src/db/passwords.txt", "r").read().split()
        # logins = ("user2",)
        # passwords = ("12345",)
        self.brute_force.bruteforce(logins, passwords)

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
        # print("Admin: ", self.wp_site.admin)
        # print("Is Readme: ", self.wp_site.is_readme)
        # print("Is Installed: ", self.wp_site.is_installed)
        # print("Is WP: ", self.wp_site.is_wp)
        print("Is HTTPS: ", self.wp_site.http_ver)
        print("Requests to API remaining: ", self.wps_api.requests_to_api_remaining)
        # print("Is Robots: ", self.wp_site.is_robots)
        # print("Is Sitemap: ", self.wp_site.is_sitemap)
        # print("Is Favicon: ", self.wp_site.is_favicon)
        # print("Is Login: ", self.wp_site.is_login)
        # print("Is Admin: ", self.wp_site.is_admin)
        # print("Is XMLRPC: ", self.wp_site.is_xmlrpc)
