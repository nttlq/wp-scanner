import requests
import re
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import concurrent.futures
import multiprocessing

import urllib3

from main import Scanner

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# список логинов и паролей
logins = open("src/db/logins.txt", "r").read().split()
passwords = open("src/db/passwords.txt", "r").read().split()
print("logins:", logins)
# URL для авторизации в WordPress
login_url = "http://curse.local/wp-login.php"


class Parser:
    def warning(func):
        def wrapper(*args):
            return str(func(*args))

        return wrapper

    def __init__(self, scanner) -> None:
        # self.scanner = scanner
        self.url = scanner.url
        self.user_agent = scanner.user_agent
        self.users = scanner.users

    def get_users(self):
        route = "/?rest_route=/wp/v2/users"

        response = requests.get(
            self.url + route,
            headers={"User-Agent": self.user_agent},
            verify=False,
        )
        # response = requests.get(url + "/wp-json/wp/v2/users")
        users = response.json()
        # print(users[0]["name"])

        print("[*] Found users:")  # , [user["name"] for user in users])
        for user in users:
            self.users.add(user["name"])
            print(user["name"])

    pass


a = Scanner("http://curse.local")
b = Parser(a)
b.get_users()
print(a.users)

while True:
    pass


def check_login(
    session,
    login,
    password,
):
    # session = requests.Session()
    data = {"log": login, "pwd": password, "wp-submit": "Log In"}
    response = session.post(login_url, data=data)
    temp_soup = BeautifulSoup(response.text, "html.parser")
    # print(temp_soup.text)
    login_error_div = temp_soup.find("div", {"id": "login_error"})

    themes_url = "http://curse.local/wp-admin/themes.php"
    response1 = session.get(themes_url, verify=False)
    temp_soup1 = BeautifulSoup(response1.text, "html.parser")
    themes = temp_soup1.find_all("div", class_="theme")
    for theme in themes:
        # print(theme)
        # Находим тег h2 с классом "theme-name"
        h2 = theme.find("h2", class_="theme-name")

        # Получаем значение атрибута "id" и очищаем его от пробелов
        theme_id = h2.get("id").strip()

        # Получаем текст из тега h2 и очищаем его от пробелов
        theme_name = h2.text.strip()
        span = h2.find("span")
        # Находим тег img внутри тега div с классом "theme-screenshot"
        img = theme.find("div", class_="theme-screenshot").find("img")
        # Получаем значение атрибута "src" и разделяем его по символу "="
        src_parts = img["src"].split("=")

        # Получаем последнюю часть разделенной строки, которая содержит номер версии
        version = src_parts[-1]

        print("Theme name: {}; Theme id: {}".format(theme_name, theme_id))
        print("Version: {}".format(version))
    if login_error_div:
        error_message = login_error_div.text.strip()
        print(f"Login failed with message: {error_message}")
        session.close()
        return False
    else:
        admin_bar = temp_soup.find("body").find("div", {"id": "wpadminbar"})
        if admin_bar:
            print(f"Successful login with {login}:{password} (admin)")
            temp_login = login
            temp_password = password
            session.close()
            return True
        else:
            print(f"Successful login with {login}:{password} (not admin)")
            session.close()

            return False


with requests.Session() as s:
    check_login(s, "admin", "admin")
# создаем пул потоков с максимальным количеством воркеров 10
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    # перебираем все логины
    with requests.Session() as session:  ########################
        for login in logins:
            if executor._shutdown:
                break
            # создаем список задач для текущего логина
            tasks = []
            # перебираем все пароли
            for password in passwords:
                # добавляем задачу в список задач
                task = executor.submit(check_login, session, login, password)
                # добавляем задачу в список только в том случае, если все предыдущие задачи для данного логина не были выполнены
                if not any(task.result() for task in tasks):
                    tasks.append(task)

                else:
                    # завершаем выполнение всех задач для текущего логина, если был найден успешный логин
                    executor.shutdown(wait=True)
                    break
                    # pass


print("НАЧАЛ ПОИСК ЛЮДЕЙ")
# URL сайта, который нужно проанализировать
url = "http://curse.local"
# # отправка GET-запроса на сайт и получение содержимого страницы
response = requests.get(url + "/?rest_route=/wp/v2/users")
# response = requests.get(url + "/wp-json/wp/v2/users")
users = response.json()
# print(users[0]["name"])

print("[*] Found users:")  # , [user["name"] for user in users])
for user in users:
    print(user["name"])
print("ЗАКОНЧИЛ ПОИСК ЛЮДЕЙ")
soup = BeautifulSoup(response.content, "html.parser")

# import requests

# Create a session object
s = requests.Session()

# Define the login URL, username, and password
login_url = "http://curse.local/wp-login.php"
username = "admin"
password = "12345"

# Create a dictionary with the login data
login_data = {
    "log": username,
    "pwd": password,
    "wp-submit": "Войти",
    "redirect_to": "http://curse.local/wp-admin/",
    "testcookie": "1",
}

# Make a POST request to the login URL with the login data as the json parameter
wp_login = "http://curse.local/wp-login.php"
wp_admin = "http://curse.local/wp-admin/"
username = "admin"
password = "admin"

with requests.Session() as s:
    headers1 = {"Cookie": "wordpress_test_cookie=WP Cookie check"}
    datas = {
        "log": username,
        "pwd": password,
        "wp-submit": "Log In",
        "redirect_to": wp_admin,
        "testcookie": "1",
    }
    res = s.post(wp_login, headers=headers1, data=datas, verify=False)
    temp_soup = BeautifulSoup(res.text, "html.parser")
    # print(temp_soup.text)
    login_error_div = temp_soup.find("div", {"id": "login_error"})
    if login_error_div:
        error_message = login_error_div.text.strip()
        print(f"Login failed with message: {error_message}")
        session.close()
    else:
        admin_bar = temp_soup.find("body").find("div", {"id": "wpadminbar"})
        if admin_bar:
            print(f"Successful login with {username}:{password} (admin)")
            temp_login = login
            temp_password = password
            session.close()
        else:
            print(f"Successful login with {username}:{password} (not admin)")
            session.close()

    resp = s.get(wp_admin)
    # print(resp.text)
# while True:
#    pass
print("НАЧАЛ ПОИСК ТЕМ")
with requests.Session() as session:  ########################
    data = {"log": "admin", "pwd": "12345", "wp-submit": "Log In"}

    session.post(login_url, data=data, verify=False)
    themes_url = "http://curse.local/wp-admin/themes.php"
    response = session.get(themes_url, verify=False)
    # Используем библиотеку BeautifulSoup для парсинга HTML-страницы
    soup = BeautifulSoup(response.text, "html.parser")
    print(session.cookies)
    # Находим все элементы с классом "theme" на странице
    themes = soup.find_all("div", class_="theme")
    for theme in themes:
        # print(theme)
        # Находим тег h2 с классом "theme-name"
        h2 = theme.find("h2", class_="theme-name")

        # Получаем значение атрибута "id" и очищаем его от пробелов
        theme_id = h2.get("id").strip()

        # Получаем текст из тега h2 и очищаем его от пробелов
        theme_name = h2.text.strip()
        span = h2.find("span")
        # Находим тег img внутри тега div с классом "theme-screenshot"
        img = theme.find("div", class_="theme-screenshot").find("img")
        # Получаем значение атрибута "src" и разделяем его по символу "="
        src_parts = img["src"].split("=")

        # Получаем последнюю часть разделенной строки, которая содержит номер версии
        version = src_parts[-1]

        print("Theme name: {}; Theme id: {}".format(theme_name, theme_id))
        print("Version: {}".format(version))
print("ВСЕ ТЕМЫ")


print("НАЧАЛ ПОИСК ПЛАГИНОВ")
with requests.Session() as session:  ########################
    data = {"log": "admin", "pwd": "12345", "wp-submit": "Log In"}

    session.post(login_url, data=data, verify=False)
    plugins_url = "http://curse.local/wp-admin/plugins.php"
    response = session.get(plugins_url)
    # Используем библиотеку BeautifulSoup для парсинга HTML-страницы
    soup = BeautifulSoup(response.text, "html.parser")

    # Находим все элементы с классом "plugins" на странице
    plugins = soup.find_all("div", class_="active second plugin-version-author-uri")

    for plugin in plugins:
        # Получение версии плагина
        version = plugin.find(string=lambda text: "Версия" in text)
        version = version.split(" ")[1]

        # Получение названия плагина
        plugin_name = plugin.find("a", {"class": "thickbox open-plugin-details-modal"})[
            "data-title"
        ]
        headers = {
            "Authorization": "Token token=sST2gat5Bnsv9mGnUjD4zugVhRMByqmBt6eYOaOXMxc"
        }
        vulnerabilities_url = "https://wpscan.com/api/v3/plugins/"
        # x='1-flash-gallery'
        vulnerability_respons = requests.get(vulnerabilities_url, headers=headers)
        # print(vulnerability_respons.text)
        # проверка каждого найденного плагина на наличие уязвимостей
        vulnerability_response = requests.get(
            vulnerabilities_url + plugin_name.replace(" ", "-").lower(), headers=headers
        )

        if vulnerability_response:
            vulnerabilities = vulnerability_response.json()
            vulnerabilities = vulnerabilities[plugin_name.replace(" ", "-").lower()]
            if "error" in vulnerabilities:
                print(f'[-] Error: {vulnerabilities["error"]}')
            if vulnerabilities["vulnerabilities"]:
                print(
                    f'[!] Found {vulnerabilities["vulnerabilities"]} vulnerabilities in plugin {plugin_name.replace(" ","-").lower()}'
                )
                for vulnerability in vulnerabilities["data"]:
                    print(f'    - {vulnerability["title"]}')
            #
            else:
                print(
                    f'[!] No vulnerabilities found in plugin {plugin_name.replace(" ", "-")}'
                )

        print("Plugin name: {}".format(plugin_name))
        print("Version: {}".format(version))
print("ВСЕ ПЛАГИНЫ")


print("Проверка на наличие")
# Все что выше работает
url = "http://curse.local"
response = requests.get(url)
html = response.content
soup = BeautifulSoup(html, "html.parser")
inputs = soup.find_all("input")
if inputs == []:
    print("Нет символов для SQl инекции")

for input in inputs:
    if "type" in input.attrs and input.attrs["type"] == "text":
        name = input.attrs["name"]
        value = input.attrs["value"]
        # Проверяем, есть ли в значении поля какие-то необычные символы, которые могут быть использованы для инъекций
        if value and not value.isnumeric() and not value.isalpha():
            print(
                f"Possible SQL injection vulnerability in input field {name} with value {value}"
            )


# поиск всех ссылок на странице


# ntvs
# for link in soup.find_all('a'):
#     href = link.get('href')
#     print(href)
#     print("____________________")
#     if href:
#         if 'wp-json/wp/v2/users' in href:  # если на странице есть ссылка на REST API WordPress
#             user_response = requests.get(href)
#             users = user_response.json()
#             print(users)
#             print('[*] Found users: ', [user['name'] for user in users])  # вывод имен найденных пользователей
#         elif '/wp-content/themes/' in href:  # если на странице есть ссылка на тему WordPress
#             theme_name = href.split('/wp-content/themes/')[1].split('/')[0]  # извлечение названия темы
#             print('[*] Found theme:', theme_name)  # вывод названия найденной темы


#
# print("НАЧАЛ ПОИСК ТЕМ")
# # URL базы данных уязвимостей тем WordPress
# vulnerabilities_url = 'https://wpscan.com/themes'
#
# # проверка каждой найденной темы на наличие уязвимостей
# for link in soup.find_all('a'):
#     href = link.get('href')
#     if '/wp-content/themes/' in href:
#          theme_name = href.split('/wp-content/themes/')[1].split('/')[0]
#          vulnerability_response = requests.get(vulnerabilities_url + theme_name)
#          vulnerabilities = vulnerability_response.json()
#          if 'error' in vulnerabilities:
#              print(f'[-] Error: {vulnerabilities["error"]}')
#          elif vulnerabilities['total'] > 0:
#              print(f'[!] Found {vulnerabilities["total"]} vulnerabilities in theme {theme_name}')
#              for vulnerability in vulnerabilities['data']:
#                   print(f'    - {vulnerability["title"]}')
#
# # URL сайта, который нужно проанализировать
# print("НАЧАЛ ПОИСК СОДЕРЖИМОГО")
#
# response = requests.get(url)
# soup = BeautifulSoup(response.content, 'html.parser')
#
# # поиск всех ссылок на странице
# for link in soup.find_all('link'):
#     href = link.get('href')
#     if 'plugins' in href:
#         plugin_name = href.split('/plugins/')[1].split('/')[0]  # извлечение названия плагина
#         plugin_response = requests.get(href)
#         plugin_soup = BeautifulSoup(plugin_response.content, 'html.parser')
#         plugin_version = plugin_soup.find('span', {'class': 'plugin-version-author-uri'}).text.split(' ')[1]  # извлечение версии плагина
#         print(f'[*] Found plugin: {plugin_name} (version: {plugin_version})')  # вывод названия и версии найденного плагина
# print("НАЧАЛ ПОИСК ПЛАГИНОВ")
# # URL базы данных уязвимостей плагинов WordPress
# vulnerabilities_url = 'https://wpscan.com/plugins'
#
# # проверка каждого найденного плагина на наличие уязвимостей
# if 'plugins' in href:
#     plugin_name = href.split('/plugins/')[1].split('/')[0]
#     vulnerability_response = requests.get(vulnerabilities_url + plugin_name)
#     vulnerabilities = vulnerability_response.json()
#     if 'error' in vulnerabilities:
#         print(f'[-] Error: {vulnerabilities["error"]}')
#     elif vulnerabilities['total'] > 0:
#         print(f'[!] Found {vulnerabilities["total"]} vulnerabilities in plugin {plugin_name}')
#         for vulnerability in vulnerabilities['data']:
#             print(f'    - {vulnerability["title"]}')
# print("все")
#
#
#
# response = requests.get(url)
# soup = BeautifulSoup(response.content, 'html.parser')
#
# plugins = []
#
# for script_tag in soup.find_all('script'):
#     if script_tag.get('src') and 'plugins' in script_tag.get('src'):
#         plugins.append(script_tag.get('src'))
#
# print('Found plugins: ', plugins)
#
#
#
# url = 'http://curse.local/wp-content/plugins/akismet/'
# response = requests.get(url)
#
# pattern = r'Version: (\d+\.\d+(\.\d+)?)'
# match = re.search(pattern, response.text)
#
# if match:
#     print('Found version: ', match.group(1))
# else:
#     print('Version not found.')


# Отправляем GET запрос на главную страницу сайта
# response = requests.get(url)
#
# # Парсим HTML страницу с помощью BeautifulSoup
# soup = BeautifulSoup(response.text, "html.parser")
#
# # Ищем тег <link> с атрибутом rel="stylesheet"
# stylesheets = soup.find_all("link", {"rel": "stylesheet"})
#
# # Ищем тег <script> с атрибутом src, содержащим "plugins"
# plugins = soup.find_all("script", {"src": lambda src: "plugins" in src})
#
# # Ищем тег <script> с атрибутом src, содержащим "jquery"
# jquery = soup.find_all("script", {"src": lambda src: "jquery" in src})
#
# # Выводим результаты
# print("Стили:")
# for stylesheet in stylesheets:
#     print(stylesheet.get("href"))
#
# print("Плагины:")
# for plugin in plugins:
#     print(plugin.get("src"))
#
# print("jQuery:")
# for jq in jquery:
#     print(jq.get("src"))


# from wordpress_xmlrpc import Client
# from wordpress_xmlrpc.methods import themes
#
#
# def get_all_themes(url, username, password):
#     wp = Client(url + 'xmlrpc.php', username, password)
#     all_themes = wp.call(themes.GetThemes())
#     return all_themes
#
#
# def get_vulnerable_themes(url, username, password):
#     all_themes = get_all_themes(url, username, password)
#     vulnerable_themes = []
#     for theme in all_themes:
#         if theme.version in vulnerable_themes:
#             continue
#         # проверка на уязвимости темы
#         if is_vulnerable(theme):
#             vulnerable_themes.append(theme.version)
#     return vulnerable_themes
#
#
# def is_vulnerable(theme):
#     # проверка на уязвимости темы
#     return False  # замените на свою функцию проверки уязвимости
