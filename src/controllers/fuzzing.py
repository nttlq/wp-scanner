import requests
import keyboard


class Fuzzing:
    def __init__(self, wp_site):
        self.__url = wp_site.url
        self.__filepath = "src/db/"
        self.themes = wp_site.themes
        self.plugins = wp_site.plugins
        self.files = wp_site.files
        self.__stop = False  # Add a stop flag

    def stop(self, e=None):  # Add a method to set the stop flag
        self.__stop = True

    @property
    def url(self):
        return self.__url

    @property
    def filepath(self):
        return self.__filepath

    def fuzzing_themes(self):
        keyboard.on_press_key("q", self.stop)  # Stop on 'q' key press
        with open(self.filepath + "wp_themes.txt") as themes:
            themes = themes.readlines()

            for theme in themes:
                print(theme)
                if self.__stop:
                    print("Fuzzing stopped.")
                    self.__stop = False
                    break
                theme = theme.strip()
                complete_url = self.url + theme + "style.css"
                res = requests.get(complete_url, verify=False)
                if res.status_code == 200:
                    self.themes[theme.split("/")[-2]] = "vulns Not found"

    def fuzzing_plugins(self):
        keyboard.on_press_key("q", self.stop)  # Stop on 'q' key press

        with open(self.filepath + "wp_plugins.txt") as plugins:
            plugins = plugins.readlines()

            for plugin in plugins:
                print(plugin)
                if self.__stop:
                    print("Fuzzing stopped.")
                    self.__stop = False
                    break
                plugin = plugin.strip()
                complete_url = self.url + plugin
                res = requests.get(complete_url, verify=False)
                if res.status_code == 200:
                    self.plugins[plugin.split("/")[-2]] = "vulns Not found"

    def fuzzing_components(self):
        keyboard.on_press_key("q", self.stop)  # Stop on 'q' key press

        with open(self.filepath + "wp_components.txt") as components:
            components = components.readlines()

            for component in components:
                print(component)
                if self.__stop:
                    print("Fuzzing stopped.")
                    self.__stop = False
                    break
                print(component)
                component = component.strip()
                complete_url = self.url + component
                res = requests.get(complete_url, verify=False)
                if res.status_code == 200:
                    self.files.add(component)


if __name__ == "__main__":

    class WP:
        def __init__(self) -> None:
            self.url = "https://curse.local/"
            self.ports = {}
            self.themes = {}
            self.plugins = {}
            self.files = set()

    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    wp_site = WP()
    fz = Fuzzing(wp_site)
    fz.fuzzing_themes()
    print(wp_site.themes)
    print(wp_site.plugins)
    print(wp_site.files)
