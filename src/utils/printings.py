from colorama import Fore, Style


class Printer:
    def warning(func):
        def wrapper(*args):
            return Fore.YELLOW + str(func(*args)) + Style.RESET_ALL

        return wrapper

    def error(func):
        def wrapper(*args):
            return Fore.RED + str(func(*args)) + Style.RESET_ALL

        return wrapper

    def info(func):
        def wrapper(*args):
            return Fore.CYAN + str(func(*args)) + Style.RESET_ALL

        return wrapper

    def debug(func):
        def wrapper(*args):
            return Fore.MAGENTA + str(func(*args)) + Style.RESET_ALL

        return wrapper

    def success(func):
        def wrapper(*args):
            return Fore.GREEN + str(func(*args)) + Style.RESET_ALL

        return wrapper

    @staticmethod
    @success
    def hello() -> str:
        string = ""
        string += r" __      ___ __        ___  ___ __ _ _ __  _ __   ___ _ __ " + "\n"
        string += r" \ \ /\ / / '_ \ _____/ __|/ __/ _` | '_ \| '_ \ / _ \ '__|" + "\n"
        string += r"  \ V  V /| |_) |_____\__ \ (_| (_| | | | | | | |  __/ |   " + "\n"
        string += r"   \_/\_/ | .__/      |___/\___\__,_|_| |_|_| |_|\___|_|   " + "\n"
        string += r"          |_|                                            " + "\n"
        return string

    @staticmethod
    @warning
    def author() -> str:
        string = ""
        string += "Created by\n"
        string += (
            r"  _____ _                           _    _             _ _            "
            + "\n"
        )
        string += (
            r" |_   _(_)_ __ ___  _   _ _ __     / \  (_)_ __  _   _| | | _____   __"
            + "\n"
        )
        string += (
            r"   | | | | '_ ` _ \| | | | '__|   / _ \ | | '_ \| | | | | |/ _ \ \ / /"
            + "\n"
        )
        string += (
            r"   | | | | | | | | | |_| | |     / ___ \| | | | | |_| | | | (_) \ V /"
            + "\n"
        )
        string += (
            r"   |_| |_|_| |_| |_|\__,_|_|    /_/   \_\_|_| |_|\__,_|_|_|\___/ \_/"
            + "\n"
        )
        return string

    @staticmethod
    def print_all():
        print(Printer.hello())
        print(Printer.author())


if __name__ == "__main__":
    Printer.print_all()

    @Printer.error
    def print_str():
        str1 = 12

        return str1

    str1 = "Hello, World!"

    print(print_str())
