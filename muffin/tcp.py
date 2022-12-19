import socket
import re
from pyroute2 import IPRoute
from dictor import dictor
from muffin.shared import RED, GREEN, RESET, _get_cfg

cfg = _get_cfg()

def check_not_hostname(ip):
    """checks if IP is ipv4 and not a hostname"""
    regex = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    return regex.match(ip)

def get_route(ip):
    """returns the route gateway of an IP address"""

    route = None

    if check_not_hostname(ip):
        with IPRoute() as ipr:
            for rt in ipr.get_routes(family=socket.AF_INET, dst=ip):
                for r in dictor(rt, "attrs"):
                    if r[0] == "RTA_GATEWAY":
                        route = r[1]
    if route:
        return route
    else:
        return "N/A"


def tcp(ip, port, feed, group, q, args, result):
    """test TCP connectivity from host"""

    count = q.get()

    # check if hostname or IP, if hostname, get actual IP of target
    try:
        socket.inet_aton(ip)
        ip_addr = ip
    except socket.error:
        try:
            ip_addr = socket.gethostbyname(ip)
        except socket.gaierror:
            print(f"[tcp] {RED}IP is invalid: {ip}{RESET}")
            return
    except TypeError:
        print(f"[tcp] {RED}IP is invalid: {ip} type error{RESET}")
        return

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(cfg['tcp_timeout'])
    conn_result = s.connect_ex((ip_addr, int(port)))
    s.close()
    route = get_route(ip)

    # connection return code
    return_code = {
        "111": ["Refused", f"{RED}"],
        "11": ["Timeout", f"{RED}"],
        "0": ["Received", f"{GREEN}"],
    }

    status = dictor(return_code, f"{conn_result}.0")

    result[count] = {
        "name": f"[tcp] {group} {feed}",
        "status": status,
        "ip": f"{ip}:{port}",
        "route": f"{route}",
    }

    q.task_done()
    return result
