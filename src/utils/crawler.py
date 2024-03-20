from urllib.parse import urljoin
import threading

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import url_changes
import keyboard


class Crawler:
    def __init__(self, wp_site):
        self.__url: str = wp_site.url
        self.visited_urls: set[str] = wp_site.linked_urls
        self.max_depth: int = 2
        self.to_visit: list[tuple[str, int]] = [(self.url, 0)]
        self.lock = threading.Lock()
        self.injection_urls: set[str] = wp_site.injection_urls
        self.all_forms: list[dict] = wp_site.all_forms
        self.__stop = False

    def stop(self, e=None):
        self.__stop = True

    @property
    def url(self) -> str:
        return self.__url

    def __visit_url(self, current_url, depth) -> None:
        if current_url in self.visited_urls or depth > self.max_depth:
            return
        try:
            res = requests.get(current_url, timeout=20.5, verify=False)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            links = [
                urljoin(current_url, link.get("href"))
                for link in soup.find_all("a")
                if link.get("href")
            ]
            self.to_visit.extend([(link, depth + 1) for link in links])
            self.visited_urls.add(current_url)

        except requests.exceptions.RequestException as e:
            print(f"Error in request to {current_url}: {e}")

    def crawl_website(self, max_depth: int = None):
        if max_depth:
            if type(max_depth) != int:
                raise TypeError("max_depth must be an integer")

            if max_depth < 0:
                raise ValueError("max_depth must be a positive integer")

            self.max_depth = max_depth

        threads = []
        while self.to_visit or threads:
            self.lock.acquire()
            if not self.to_visit:
                self.lock.release()
                threads = [t for t in threads if t.is_alive()]
                continue

            current_url, depth = self.to_visit.pop()
            self.lock.release()
            t = threading.Thread(target=self.__visit_url, args=(current_url, depth))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    def detect_forms(self, url):
        soup = BeautifulSoup(requests.get(url, verify=False).content, "html.parser")
        return soup.find_all("form")

    def get_form_details(self, form):
        detailsOfForm = {}
        action = form.attrs.get("action")
        method = form.attrs.get("method", "get")
        inputs = []

        for input_tag in form.find_all("input"):
            input_type = input_tag.attrs.get("type", "text")
            input_name = input_tag.attrs.get("name")
            input_value = input_tag.attrs.get("value", "")
            inputs.append(
                {
                    "type": input_type,
                    "name": input_name,
                    "value": input_value,
                }
            )

        detailsOfForm["action"] = action
        detailsOfForm["method"] = method
        detailsOfForm["inputs"] = inputs
        return detailsOfForm

    def detect_all_forms(self, url):
        forms = self.detect_forms(url)
        for form in forms:
            details = self.get_form_details(form)
            self.all_forms.append(details)

    def find_injection_urls(self, main_url_only: bool = None):
        keyboard.on_press_key("q", self.stop)

        if main_url_only is None or main_url_only is False:
            if self.visited_urls:
                visited_urls = self.visited_urls
            else:
                visited_urls = {self.url}
        else:
            visited_urls = {self.url}

        driver = webdriver.Firefox()

        for url in visited_urls:
            if self.__stop:
                print("Crawling stopped.")
                self.__stop = False
                break
            self.detect_all_forms(url)

            print("URL:", url)
            driver.get(url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            search_boxes = driver.find_elements(By.TAG_NAME, "input")

            for i in range(len(search_boxes)):
                if self.__stop:
                    print("Crawling stopped.")
                    self.__stop = False
                    return
                driver.get(url)

                # Wait for the page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                search_box = driver.find_elements(By.TAG_NAME, "input")[i]

                # Type the search query
                try:
                    search_box.send_keys("tsqlit")
                    # Submit the form
                    search_box.submit()
                    # Wait for the URL to change
                    WebDriverWait(driver, 10).until(url_changes(driver.current_url))

                    # Print the current URL
                    current_url = driver.current_url
                    if "?" in current_url:
                        self.injection_urls.add(current_url.replace("=tsqlit", "="))
                except Exception as e:
                    print(f"An exception occurred: {e}")
                    continue

        # Close the driver
        driver.quit()


if __name__ == "__main__":
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    class Wp_Site:
        def __init__(self):
            self.url = "http://127.0.0.1:5000"
            self.linked_urls = set()
            self.injection_urls = set()
            self.all_forms = []

    wp = Wp_Site()
    site = Crawler(wp)
    site.crawl_website(2)
    print(site.visited_urls)

    site.find_injection_urls()
    print(site.injection_urls)
