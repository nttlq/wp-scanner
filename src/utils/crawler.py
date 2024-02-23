from urllib.parse import urljoin
import threading

import requests
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self, wp_site):
        self.__url: str = wp_site.url
        self.visited_urls: set[str] = wp_site.linked_urls
        self.max_depth: int = 2
        self.to_visit: list[tuple[str, int]] = [(self.url, 0)]
        self.lock = threading.Lock()

    @property
    def url(self) -> str:
        return self.__url

    def __visit_url(self, current_url, depth) -> None:
        if current_url in self.visited_urls or depth > self.max_depth:
            return
        try:
            res = requests.get(current_url, timeout=2.5, verify=False)
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
            print(f"Ошибка при обращении к {current_url}: {e}")

    def crawl_website(self, max_depth: int = None):
        if max_depth:
            if type(max_depth) != int:
                raise TypeError("max_depth должен быть целым числом")

            if max_depth < 0:
                raise ValueError("max_depth должен быть неотрицательным числом")

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


if __name__ == "__main__":
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    class Wp_Site:
        def __init__(self):
            self.url = "https://curse.local"
            self.linked_urls = set()

    wp = Wp_Site()
    site = Crawler(wp)
    site.crawl_website()
    print(site.visited_urls)
