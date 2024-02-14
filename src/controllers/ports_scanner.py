import sys
import socket
from datetime import datetime
from ipaddress import ip_address

import pyfiglet


class PortScanner:
    def __init__(self, wp_site):
        self.__url: str = wp_site.url
        self.ips = self.get_ips(self.url)
        self.ports = []
        self.ports_range = (1, 65535)

    @property
    def url(self):
        return self.__url

    def is_private_ip_address(IP: str) -> bool:
        return True if (ip_address(IP).is_private) else False

    def get_ips(self) -> list:
        try:
            ips = socket.gethostbyname_ex(self.url)
        except socket.gaierror:
            ips = []
        return ips[2]

    def scan_ports(self, ports_range: tuple = (1, 7), port=None):
        try:
            # will scan ports between 1 to 65,535
            for port in range(1, ports_range):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket.setdefaulttimeout(1)

                # returns an error indicator
                result = s.connect_ex((target, port))
                if result == 0:
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


site = ("dfiles.ru", "torquemag.io")
ips = get_ips_for_host(site[1])
for ip in ips:
    print(repr(ip))
    print(is_private_ip_address(ip))
# ('www.l.google.com', [], ['74.125.77.104', '74.125.77.147', '74.125.77.99'])


import socket

h_name = socket.gethostname()
IP_addres = socket.gethostbyname(h_name)
print("Host Name is:" + h_name)
print("Computer IP Address is:" + IP_addres)
print("Public IP Address is:", is_private_ip_address(IP_addres))


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
