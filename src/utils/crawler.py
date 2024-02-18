import requests
from bs4 import BeautifulSoup

# import networkx as nx
# import matplotlib.pyplot as plt
from urllib.parse import urlparse, urljoin


# Функция для краулинга веб-сайта с обработкой ошибок
def crawl_website(url, max_depth=3):
    visited_urls = set()
    to_visit = [(url, 0)]

    while to_visit:
        current_url, depth = to_visit.pop()
        if current_url in visited_urls or depth > max_depth:
            continue

        try:
            # Проверка и добавление схемы, если ее нет
            parsed_url = urlparse(current_url)
            if not parsed_url.scheme:
                current_url = "http://" + current_url  # Можно также использовать https

            # Загрузка страницы
            response = requests.get(current_url)
            response.raise_for_status()  # Проверка на ошибки HTTP

            # Парсинг HTML-кода страницы
            soup = BeautifulSoup(response.text, "html.parser")

            # Извлечение ссылок
            links = [
                urljoin(current_url, link.get("href"))
                for link in soup.find_all("a")
                if link.get("href")
            ]

            # Добавление найденных ссылок в очередь с учетом глубины
            to_visit.extend([(link, depth + 1) for link in links])

            visited_urls.add(current_url)
            print(f"Найдена ссылка: {current_url}")

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при обращении к {current_url}: {e}")

    return visited_urls


# # Функция для построения ссылочного графа
# def build_graph(visited_urls):
#     G = nx.Graph()

#     for url in visited_urls:
#         G.add_node(url)

#     # Добавление ребер на основе найденных ссылок
#     for url in visited_urls:
#         try:
#             response = requests.get(url)
#             response.raise_for_status()
#             soup = BeautifulSoup(response.text, "html.parser")
#             links = [
#                 urljoin(url, link.get("href"))
#                 for link in soup.find_all("a")
#                 if link.get("href")
#             ]
#             G.add_edges_from([(url, link) for link in links])

#         except requests.exceptions.RequestException as e:
#             print(f"Ошибка при обращении к {url} для построения графа: {e}")

#     return G


# # Функция для проверки связности графа
# def is_connected_graph(G):
#     return nx.is_connected(G)


# # Функция для расчета индекса цитирования (PageRank)
# def calculate_page_rank(G):
#     page_rank = nx.pagerank(G)
#     return page_rank


# # Функция для поиска страниц с наибольшим индексом цитирования
# def find_top_pages(page_rank, n):
#     top_pages = sorted(page_rank.items(), key=lambda x: x[1], reverse=True)[:n]
#     return top_pages


# def find_pages_with_lowest_page_rank(page_rank, n):
#     # Используем lambda-функцию для сортировки по индексу цитирования
#     sorted_pages = sorted(page_rank.items(), key=lambda x: x[1])

#     # Получаем первые n страниц с наименьшим индексом цитирования
#     lowest_rank_pages = sorted_pages[:n]

#     return lowest_rank_pages


# # Функция для поиска кратчайших путей
# def find_shortest_paths(G, source, target):
#     shortest_paths = nx.shortest_path(G, source=source, target=target)
#     return shortest_paths

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
if __name__ == "__main__":

    start_url = "curse.local"  #  Начальный URL
    max_depth = 6  # Максимальная глубина краулинга
    top_n_pages = (
        3  # Количество страниц с наибольшим индексом цитирования для отображения
    )
    low_n_pages = 3

    # Вызов функций
    visited_urls = crawl_website(start_url, max_depth)

    print("visited: ", visited_urls)
