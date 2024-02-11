class Menu:
    @staticmethod
    @Printer.info
    def options() -> str:
        string = ""
        string += "OPTIONS" + "\n"
        string += "[1] Scanner" "\n"
        string += "[2] Brutforce" "\n"
        string += "[3] Change User-Agent" "\n"
        string += "[4] Show All info" "\n"
        return string
