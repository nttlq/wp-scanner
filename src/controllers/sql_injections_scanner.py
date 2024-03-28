import re

import requests
import keyboard


class SQLInjectionScanner:
    ERROR_PATTERNS = {
        "MySQL": (
            r"SQL syntax.*MySQL",
            r"Warning.*mysql_.*",
            r"MySQL Query fail.*",
            r"SQL syntax.*MariaDB server",
            r"SQL syntax.*?MySQL",
            r"Warning.*?\Wmysqli?_",
            r"MySQLSyntaxErrorException",
            r"valid MySQL result",
            r"check the manual that (corresponds to|fits) your MySQL server version",
            r"Unknown column '[^ ]+' in 'field list'",
            r"MySqlClient\.",
            r"com\.mysql\.jdbc",
            r"Zend_Db_(Adapter|Statement)_Mysqli_Exception",
            r"Pdo[./_\\]Mysql",
            r"MySqlException",
            r"SQLSTATE\[\d+\]: Syntax error or access violation",
        ),
        "PostgreSQL": (
            r"PostgreSQL.*ERROR",
            r"Warning.*\Wpg_.*",
            r"Warning.*PostgreSQL",
            r"PostgreSQL.*?ERROR",
            r"Warning.*?\Wpg_",
            r"valid PostgreSQL result",
            r"Npgsql\.",
            r"PG::SyntaxError:",
            r"org\.postgresql\.util\.PSQLException",
            r"ERROR:\s\ssyntax error at or near",
            r"ERROR: parser: parse error at or near",
            r"PostgreSQL query failed",
            r"org\.postgresql\.jdbc",
            r"Pdo[./_\\]Pgsql",
            r"PSQLException",
        ),
        "Microsoft SQL Server": (
            r"OLE DB.* SQL Server",
            r"(\W|\A)SQL Server.*Driver",
            r"Warning.*odbc_.*",
            r"Warning.*mssql_",
            r"Msg \d+, Level \d+, State \d+",
            r"Unclosed quotation mark after the character string",
            r"Microsoft OLE DB Provider for ODBC Drivers",
        ),
        "Microsoft Access": (
            r"Microsoft Access Driver",
            r"Access Database Engine",
            r"Microsoft JET Database Engine",
            r".*Syntax error.*query expression",
        ),
        "Oracle": (
            r"\bORA-[0-9][0-9][0-9][0-9]",
            r"Oracle error",
            r"Warning.*oci_.*",
            "Microsoft OLE DB Provider for Oracle",
        ),
        "IBM DB2": (r"CLI Driver.*DB2", r"DB2 SQL error"),
        "SQLite": (
            r"SQLite/JDBCDriver",
            r"System.Data.SQLite.SQLiteException",
            r"sqlite3.OperationalError",
            r"OperationalError",
            r"unrecognized token",
        ),
        "Informix": (r"Warning.*ibase_.*", r"com.informix.jdbc"),
        "Sybase": (r"Warning.*sybase.*", r"Sybase message"),
    }

    def __init__(self, wp_site):
        self.__url = wp_site.url
        self.injection_urls = wp_site.injection_urls
        self.sqli_vulnerable_urls = wp_site.sqli_vulnerable_urls
        self.__stop = False

    def stop(self, e=None):
        self.__stop = True

    @property
    def url(self):
        return self.__url

    def set_payloads(self, filepath="src/db/sql_payloads.txt"):
        print("Setting payloads...")
        try:
            with open(filepath, "r") as file:
                payloads = file.read().splitlines()
            return payloads
        except:
            raise FileNotFoundError("Payloads file not found.")

    def vulnerable(self, res) -> bool:
        print("Checking for Vulnerability...")
        for _, errors in self.ERROR_PATTERNS.items():
            for error in errors:
                if re.compile(error).search(res):
                    return True
        return False

    def detect_sqli_vulnerability(self, custom_payloads=None):
        print("Detecting SQL Injection Vulnerability...")
        print("Press 'q' to stop the Sqli scanning.")
        keyboard.on_press_key("q", self.stop)
        if custom_payloads:
            payloads = self.set_payloads(custom_payloads)
        else:
            payloads = self.set_payloads()

        for url in self.injection_urls:
            print("Scanning: ", url)
            for payload in payloads:
                print("Payload: ", payload)
                if self.__stop:
                    print("Sqli scanning stopped.")
                    self.__stop = False
                    break
                complete_url = url + payload
                try:
                    req = requests.get("{}".format(complete_url))
                    res = req.text

                    if self.vulnerable(res):
                        self.sqli_vulnerable_urls.add(complete_url)
                        break

                    if "SQL" in res or "sql" in res or "Sql" in res:
                        self.sqli_vulnerable_urls.add(complete_url)
                        break
                except:
                    pass


if __name__ == "__main__":
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    class Wp_Site:
        def __init__(self):
            self.url = "http://127.0.0.1:5000"
            self.sqli_vulnerable_urls = set()
            self.injection_urls = {
                "http://127.0.0.1:5000/users?role=",
                "https://curse.local/?s=",
            }

    wp = Wp_Site()
    sqli = SQLInjectionScanner(wp)
    sqli.detect_sqli_vulnerability()
    print(sqli.injection_urls)
    print(sqli.sqli_vulnerable_urls)
