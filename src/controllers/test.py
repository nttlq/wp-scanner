import socket
import argparse


def banner_grabbing1(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect((ip, port))
        sock.send(b"HEAD / HTTP/1.1\r\n\r\n")
        banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
        return banner.split("\n")[0]
    except Exception as e:
        return ""


def banner_grabbing(ip, port):
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


def scan_ports(ip):
    open_ports = []
    for port in range(21, 81):  # 1 to 1000 Scan ports between
        banner = banner_grabbing(ip, port)
        if banner:
            open_ports.append((port, banner))
    return open_ports


def main():
    parser = argparse.ArgumentParser(
        description="Extract service and version information from open ports."
    )
    parser.add_argument("ip", type=str, help="Target IP address")

    args = parser.parse_args()
    target_ip = args.ip

    open_ports = scan_ports(target_ip)

    if open_ports:
        print(f"{target_ip} Ports open at:")
        for port, banner in open_ports:
            print(f"Port {port}: {banner}")
    else:
        print(f"{target_ip} No open port found at.")


if __name__ == "__main__":
    main()
