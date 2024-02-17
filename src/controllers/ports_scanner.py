import sys
import socket
from datetime import datetime
from ipaddress import ip_address

import pyfiglet


class PortScanner:
    def __init__(self, wp_site):
        self.__url: str = wp_site.url
        self.ips = self.get_ips()
        self.ports = []

    @property
    def url(self):
        return self.__url

    def is_private_ip(self, IP: str) -> bool:
        return True if (ip_address(IP).is_private) else False

    def get_ips(self) -> list:
        try:
            ips = socket.gethostbyname_ex(self.url)
        except socket.gaierror:
            ips = []
        return ips[2]

    def scan_ports(self, port: tuple = None, *ports):
        if type(ports) == int:
            ports = list(ports)
        elif type(ports) == tuple or type(ports) == list:
            ports = list(ports)

        try:
            # will scan ports between 1 to 65,535
            for ip in self.ips:
                for port in ports:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    socket.setdefaulttimeout(1)

                    # returns an error indicator
                    result = s.connect_ex((ip, port))
                    if result == 0:
                        self.ports.append(port)
                        print("Port {} is open".format(port))
                    s.close()

        except KeyboardInterrupt:
            print("\n Exiting Program !!!!")
            sys.exit()
        except socket.gaierror:
            print("\n Hostname Could Not Be Resolved !!!!")
            sys.exit()
        except socket.error:
            print("\ Server not responding !!!!")
            sys.exit()


class WP:
    def __init__(self):
        self.url = "dfiles.ru"


if __name__ == "__main__":
    wp_site = WP()

    site = ("dfiles.ru", "torquemag.io")

    ps = PortScanner(wp_site)
    ips = ps.get_ips()
    print(ps.ips)
    for ip in ps.ips:
        print(repr(ip))
        print(ps.is_private_ip(ip))
    # ('www.l.google.com', [], ['74.125.77.104', '74.125.77.147', '74.125.77.99'])

    k = [21, 22, 25, 788, 80, 110, 443, 8080]
    k2 = list(k)
    print(k2)
    ps.scan_ports(k)
    print(ps.ports)


def another_func():
    h_name = socket.gethostname()
    IP_addres = socket.gethostbyname(h_name)
    print("Host Name is:" + h_name)
    print("Computer IP Address is:" + IP_addres)
    print("Public IP Address is:", ps.is_private_ip(IP_addres))

    ascii_banner = pyfiglet.figlet_format("PORT SCANNER")
    print(ascii_banner)

    # Defining a target
    if len(sys.argv) == 2:

        # translate hostname to IPv4
        target = socket.gethostbyname(sys.argv[1])
    else:
        print("Invalid amount of Argument")

    # Add Banner
    print("-" * 50)
    print("Scanning Target: " + target)
    print("Scanning started at:" + str(datetime.now()))
    print("-" * 50)
