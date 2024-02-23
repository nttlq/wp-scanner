import sys
import socket
from datetime import datetime
from ipaddress import ip_address
from urllib.parse import urlparse, urlunparse

import pyfiglet


class PortScanner:
    def __init__(self, wp_site):
        self.__url: str = wp_site.url
        self.ips = wp_site.ips
        self.ports = wp_site.ports
        ips = self.get_ips()
        for ip in ips:
            self.ips.append(ip)

    @property
    def url(self):
        url = urlparse(self.__url).netloc
        return url

    def is_private_ip(self, IP: str) -> bool:
        return True if (ip_address(IP).is_private) else False

    def get_ips(self) -> list:
        print("URL: ", self.url)
        try:
            ips = socket.gethostbyname_ex(self.url)
        except socket.gaierror:
            ips = []
        print("IPs: ", ips)
        return ips[2]

    def banner_grabbing(self, ip, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((ip, port))
            if port == 80 or port == 443:
                sock.send(b"HEAD / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\n\r\n")
            elif port == 21:
                sock.send(b"USER anonymous\r\n")
            elif port == 22:
                sock.send(b"SSH-2.0-OpenSSH_7.3\r\n")
            elif port == 25:
                sock.send(b"HELO " + ip.encode() + b"\r\n")
            elif port == 23:
                sock.send(
                    b"\xFF\xFD\x18\xFF\xFD\x20\xFF\xFD\x23\xFF\xFD\x27\xFF\xFA\x1F\x00\x50\x00\x18\xFF\xF0"
                )
            elif port == 3306:
                sock.send(
                    b"\x05\x00\x00\x01\x85\xa6\x03\x00\x00\x00\x00\x21\x00\x00\x00\x02\x3f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                )
            elif port == 139 or port == 445:
                sock.send(
                    b"\x00\x00\x00\x85\xff\x53\x4d\x42\x72\x00\x00\x00\x00\x18\x53\xc8\x17\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2f\x4b\x00\x00\x00\x00\x00\x31\x00\x02\x50\x43\x20\x4e\x45\x54\x57\x4f\x52\x4b\x20\x50\x52\x4f\x47\x52\x41\x4d\x20\x31\x2e\x30\x00\x02\x4c\x41\x4e\x4d\x41\x4e\x31\x2e\x30\x00\x02\x57\x69\x6e\x64\x6f\x77\x73\x20\x66\x6f\x72\x20\x57\x6f\x72\x6b\x67\x72\x6f\x75\x70\x73\x20\x33\x2e\x31\x61\x00\x02\x4c\x4d\x31\x2e\x32\x58\x30\x30\x32\x00\x02\x4c\x41\x4e\x4d\x41\x4e\x32\x2e\x31\x00\x02\x4e\x54\x20\x4c\x4d\x20\x30\x2e\x31\x32\x00"
                )
            elif port == 3389:
                sock.send(
                    b"\x03\x00\x00\x13\x0E\xE0\x00\x00\x00\x00\x00\x01\x00\x08\x00\x03\x00\x00\x00"
                )
            banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
            return banner.split("\n")[0]
        except Exception as e:
            return ""

    def scan_ports_in_range(self, port_begin: int, port_end: int):
        if port_begin > port_end:
            temp = port_begin
            port_begin = port_end
            port_end = temp

        if port_begin < 1 or port_end > 65535:
            raise ValueError("Port range must be between 1 and 65,535")

        try:
            # will scan ports between 1 to 65,535
            for ip in self.ips:
                result_ports = (
                    []
                )  # Define the variable "result_ports" before the for loop

                for port in range(
                    port_begin, port_end + 1
                ):  # Iterate over the range of ports

                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    socket.setdefaulttimeout(1)

                    # returns an error indicator
                    result = s.connect_ex((ip, port))
                    if result == 0:
                        service = socket.getservbyport(port)
                        banner = self.banner_grabbing(ip, port)
                        # if service is None:
                        # print("Service: ", service)
                        port_info = {"port": port, "service": service, "banner": banner}
                        result_ports.append(port_info)

                        print("Port {} is open".format(port))
                        print("ports: ", result_ports)
                    s.close()

                if result_ports == []:
                    result_ports = None
                if ip not in self.ports:
                    self.ports[ip] = []
                # self.ports[ip] = result_ports
                for result in result_ports:
                    self.ports[ip].append(result)
                # self.ports[ip] = result_ports

        except KeyboardInterrupt:
            print("\n Exiting Program !!!!")
            sys.exit()
        except socket.gaierror:
            print("\n Hostname Could Not Be Resolved !!!!")
            sys.exit()
        except socket.error:
            print("\n Server not responding !!!!")
            sys.exit()

    def scan_ports(self, *ports):
        if type(ports) == int:
            ports = list(ports)
        elif type(ports) == tuple or type(ports) == list:
            ports = list(ports)

        # try:
        # will scan ports between 1 to 65,535
        for ip in self.ips:
            result_ports = []
            for port in ports:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    socket.setdefaulttimeout(1)

                    # returns an error indicator
                    result = s.connect_ex((ip, port))
                    if result == 0:
                        service = socket.getservbyport(port)
                        banner = self.banner_grabbing(ip, port)
                        # if service is None:
                        # print("Service: ", service)
                        port_info = {"port": port, "service": service, "banner": banner}
                        result_ports.append(port_info)

                        print("Port {} is open".format(port))
                        print("ports: ", result_ports)
                    s.close()
                except socket.error:
                    print("\n Hostname Could Not Be Resolved !!!!")
                    # sys.exit()

            if result_ports == []:
                result_ports = None
            if ip not in self.ports:
                self.ports[ip] = []
            # self.ports[ip] = result_ports
            for result in result_ports:
                self.ports[ip].append(result)

        # except KeyboardInterrupt:
        #     print("\n Exiting Program !!!!")
        #     sys.exit()
        # except socket.gaierror as e:
        #     print("\n Hostname Could Not Be Resolved !!!!")
        #     sys.exit()
        # except socket.error as e:
        #     print("\n Server not responding !!!!")
        #     print(e)
        # sys.exit()


class WP:
    def __init__(self) -> None:
        self.url = "https://curse.local/"  # "curse.local"
        self.ports = {}


if __name__ == "__main__":
    wp_site = WP()
    ports = "80 35 22"
    # port = ports.split(" ")
    port = [int(p) for p in ports.split(" ")]
    print("Port: ", port)
    site = ("dfiles.ru", "torquemag.io")

    ps = PortScanner(wp_site)
    ips = ps.get_ips()
    print(ps.ips)
    for ip in ps.ips:
        print(repr(ip))
        print(ps.is_private_ip(ip))
    # ('www.l.google.com', [], ['74.125.77.104', '74.125.77.147', '74.125.77.99'])

    # service = socket.getservbyport(466)
    # print("Service2: ", service)

    k = [21, 22, 25, 788, 80, 110, 443, 8080]
    k2 = list(k)
    print(k2)
    ps.scan_ports(22, 80, 443, 8080)
    # ps.scan_ports_in_range(1, 100)
    print("ok:", ps.ports)


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
