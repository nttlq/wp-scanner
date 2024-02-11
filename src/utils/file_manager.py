import os
from urllib.parse import urlparse, urlunparse


class FileManager:
    def __init__(self, scanner):
        self.__folder_path = self.set_folder(scanner.url)
        self.__create_folder()

    def set_folder(self, url: str):
        url = urlparse(url).netloc
        folder_path = f"src/public/{url}"
        return folder_path

    @property
    def folder_path(self):
        return self.__folder_path

    def __create_folder(self):
        print(self.folder_path)
        try:
            os.mkdir(self.folder_path)
        except TypeError:
            print("Invalid path")
        except FileExistsError:
            print("Folder already exists")

        return True

    def create_file(self, file_name):
        file_path = f"{self.folder_path}/{file_name}"
        with open(file_path, "w") as file:
            file.write("")
        return True

    def save_file(self, file_name, file_content):
        with open(self.file_path, "w") as file:
            file.write(file_content)
        return True
