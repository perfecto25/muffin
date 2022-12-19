import socket
import struct
from ipaddress import ip_address

# from config import mc_timeout, RED, GREEN, RESET
from muffin.shared import RED, RESET, _get_cfg

cfg = _get_cfg()

def mcast(ip, port, iface, feed, group, q, result):
    """connect multicast group connectivity for each solarflare iface"""
    count = q.get()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # check if IP is multicast
    if not ip_address(ip).is_multicast:
        print(f"{group} {feed} {RED} This is not a valid Multicast IP: {ip}{RESET}")
        return 1

    try:
        sock.bind((ip, port))
    except socket.error:
        print(f"{group} {feed} {RED} Invalid Group {ip}:{port} on {iface} {RESET}")
        return 1

    if iface is "":
        mreq = struct.pack("4sl", socket.inet_aton(ip), socket.INADDR_ANY)
    else:
        mreq = socket.inet_aton(ip) + socket.inet_aton(iface)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.settimeout(cfg['mc_timeout'])

    i = 0
    while i < 1:
        try:
            data, addr = sock.recvfrom(port)
        except socket.timeout:
            result[count] = {
                "name": f"[mc] {group} {feed}",
                "status": "Timed out",
                "ip": f"{ip}:{port}",
                "iface": f"{iface}",
            }
            break
        else:
            result[count] = {
                "name": f"[mc] {group} {feed}",
                "status": "Received",
                "ip": f"{ip}:{port}",
                "iface": f"{iface}",
            }
        i += 1

    q.task_done()
    return result
