import sys
import socket
from ipaddress import ip_address
from urllib.parse import urlparse

import keyboard


class PortScanner:
    def __init__(self, wp_site):
        self.__url: str = wp_site.url
        self.ips = wp_site.ips
        self.ports = wp_site.ports
        self.__stop = False

    def stop(self, e=None):
        self.__stop = True

    @property
    def url(self):
        try:
            url = urlparse(self.__url).netloc
        except Exception as e:
            url = urlparse(self.__url).hostname
        return url

    def is_private_ip(self, IP: str) -> bool:
        if "localhost" in IP:
            return True
        return True if (ip_address(IP).is_private) else False

    def get_ips(self) -> dict:
        print("Getting IPs for: ", self.url)
        if "localhost" in self.url:
            self.ips.add(urlparse(self.__url).hostname)
            return self.ips
        try:
            ips = socket.gethostbyname_ex(self.url)
        except socket.gaierror:
            ips = []
        for ip in ips[2]:
            self.ips.add(ip)
        return self.ips

    def banner_grabbing(self, ip, port):
        print("Banner grabbing for port: ", port)
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
        print("Scanning ports in range {} - {}".format(port_begin, port_end))
        keyboard.on_press_key("q", self.stop)
        print("Press 'q' to stop scanning")

        if port_begin > port_end:
            temp = port_begin
            port_begin = port_end
            port_end = temp

        if port_begin < 1 or port_end > 65535:
            raise ValueError("Port range must be between 1 and 65,535")

        try:
            for ip in self.ips:
                result_ports = []

                for port in range(port_begin, port_end + 1):
                    print(f"Scanning port: {port} for {ip}...")
                    if self.__stop:
                        print("Port scanning stopped.")
                        self.__stop = False
                        break
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    socket.setdefaulttimeout(1)

                    result = s.connect_ex((ip, port))
                    if result == 0:
                        service = socket.getservbyport(port)
                        banner = self.banner_grabbing(ip, port)
                        port_info = {"port": port, "service": service, "banner": banner}
                        result_ports.append(port_info)

                        print("Port {} is open".format(port))
                        print(f"ports in {ip}: ", result_ports)
                    s.close()

                if result_ports == [] or result_ports == None:
                    result_ports = None
                    print("Port is not open or error occurred.")
                    return
                if ip not in self.ports:
                    self.ports[ip] = []
                for result in result_ports:
                    self.ports[ip].append(result)

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
        print("Scanning ports: ", ports)
        if type(ports) == int:
            ports = list(ports)
        elif type(ports) == tuple or type(ports) == list:
            ports = list(ports)

        for ip in self.ips:
            result_ports = []
            for port in ports:
                print(f"Scanning port: {port} for {ip}...")
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    socket.setdefaulttimeout(1)

                    result = s.connect_ex((ip, port))
                    if result == 0:
                        service = socket.getservbyport(port)
                        banner = self.banner_grabbing(ip, port)
                        port_info = {"port": port, "service": service, "banner": banner}
                        result_ports.append(port_info)

                        print("Port {} is open".format(port))
                    s.close()
                except socket.error:
                    print("\n Hostname Could Not Be Resolved !!!!")

            if result_ports == [] or result_ports == None:
                result_ports = None
                print("Port is not open or error occurred.")
                return
            if ip not in self.ports:
                self.ports[ip] = []
            for result in result_ports:
                self.ports[ip].append(result)


if __name__ == "__main__":

    class WP:
        def __init__(self) -> None:
            self.url = "localhost:5000"
            self.ports = {}
            self.ips = set()

    wp_site = WP()
    ports = "80 35 22"
    port = [int(p) for p in ports.split(" ")]
    print("Port: ", port)
    site = ("dfiles.ru", "torquemag.io")
    site1 = "https://curse.local/"
    site2 = "curse.local"
    ps = PortScanner(wp_site)
    ips = ps.get_ips()
    print(ps.ips)
    for ip in ps.ips:
        print(repr(ip))
        print(ps.is_private_ip(ip))
    k = [21, 22, 25, 788, 80, 110, 443, 8080]
    k2 = list(k)
    print(k2)
    ps.scan_ports(22, 80, 443, 8080)
    print("ok:", ps.ports)
