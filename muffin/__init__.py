from collections import OrderedDict
import threading
from queue import Queue
from dictor import dictor
from muffin.mcast import mcast
from muffin.tcp import tcp
from muffin.shared import (
    RED,
    WHITE,
    GREEN,
    PURPLE,
    CYAN,
    ORANGE,
    RESET,
    _get_ifaces,
    _get_cfg,
    hostname
)


cfg = _get_cfg()

mc_errors = []
tcp_errors = []
udp_errors = []


def get_ip_port(ftype, data, group, feed):
    """returns [ip, port]"""

    ret = []

    line = dictor(data, f"{ftype}.{group}.{feed}")

    # check if string is ip:port format
    if ":" in line:
        ip = line.split(":")[0]
        plist = []
        port = line.split(":")[1]
        plist.append(port)
        ret.append(ip)
        ret.append(plist)

    # check if string is { 'ip': IP, 'port': port } format
    else:
        ip = dictor(data, f"{ftype}.{group}.{feed}.ip", checknone=True)
        ret.append(ip)

        ports = dictor(data, f"{ftype}.{group}.{feed}.port", checknone=True)
        plist = []

        # if multiple ports
        if "," in str(ports):
            p = ports.split(",")
            p = list(set(sorted(p)))
            p = filter(None, p)

            for port in sorted(p):
                if type(port) is str:
                    port = port.strip()
                    plist.append(port)
            ret.append(plist)

        # if range of ports
        elif "-" in str(ports):
            minval = ports.split("-")[0]
            maxval = int(ports.split("-")[1]) + 1
            for p in range(int(minval), int(maxval)):
                plist.append(p)
            ret.append(plist)

        # if single port
        else:
            plist.append(ports)
            ret.append(plist)

    return ret


def run_mcast(data):

    if dictor(data, "multicast"):
        print(
            f"\n{WHITE}Checking Multicast connectivity - timeout: {cfg['mc_timeout']} sec{RESET}"
        )
        count = 0
        threads = []
        q = Queue(maxsize=200)
        result = OrderedDict()

        for group in dictor(data, "multicast"):
            try:
                for feed in dictor(data, f"multicast.{group}"):
                    ret = get_ip_port("multicast", data, group, feed)
                    ip = ret[0]
                    ports = ret[1]

                    if dictor(data, f"multicast.{group}.{feed}.iface"):
                        ifaces = []
                        ifaces.append(dictor(data, f"multicast.{group}.{feed}.iface"))
                    else:
                        # get iface IPs either from config file or from host itself
                        ifaces = dictor(cfg, f"hosts.{hostname}.ifaces")
                        if not ifaces:
                            ifaces = _get_ifaces("solarflare")

                    for iface in ifaces:
                        for port in ports:
                            try:
                                port = int(port)
                            except Exception as exc:
                                print(f"{RED}Invalid port {port}{RESET}")
                                return
                            q.put(count)
                            result[count] = {}
                            thread = threading.Thread(
                                target=mcast,
                                args=(
                                    ip,
                                    port,
                                    iface,
                                    feed,
                                    group,
                                    q,
                                    result,
                                ),
                            )
                            thread.start()
                            threads.append(thread)
                            count += 1

            except Exception as exc:
                print(f"{ORANGE}WARNING:{RESET} {group} -- {exc}")
                pass

        q.join()

        for t in threads:
            t.join()

        for count, data in result.items():

            if data["status"] == "Received":
                print(
                    f'{count} {data["name"]} {GREEN}Received {data["ip"]} on {data["iface"]} {RESET}'
                )
            elif data["status"] == "Timed out":
                print(
                    f'{count} {data["name"]} {RED}Timed out {data["ip"]} on {data["iface"]} {RESET}'
                )


def run_tcp(data, args):
    if dictor(data, "tcp"):

        print(
            f"\n\n{WHITE}Checking TCP connectivity - timeout: {cfg['tcp_timeout']} sec{RESET}"
        )

        count = 0
        threads = []
        q = Queue(maxsize=200)
        result = OrderedDict()

        for group in dictor(data, "tcp"):
            try:
                for feed in dictor(data, f"tcp.{group}"):
                    ret = get_ip_port("tcp", data, group, feed)
                    ip = ret[0]
                    ports = ret[1]

                    for port in ports:
                        try:
                            port = int(port)
                        except Exception as exc:
                            print(f"{RED}Invalid port {port}{RESET}")
                            return

                        q.put(count)

                        # set ordered dict
                        result[count] = {}

                        thread = threading.Thread(
                            target=tcp,
                            args=(ip, port, feed, group, q, args, result),
                        )
                        thread.start()
                        threads.append(thread)
                        count += 1
            except Exception as exc:
                print(f"{ORANGE}WARNING:{RESET} {group} -- {exc}")
                pass

        q.join()

        for t in threads:
            t.join()

        for count, data in result.items():
            if data["status"] == "Timeout":
                print(
                    f'{count} {data["name"]} {RED}Timeout {data["ip"]}{RESET} {CYAN}via {data["route"]}{RESET}'
                )
            elif data["status"] == "Refused":
                print(
                    f'{count} {data["name"]} {RED}Refused {data["ip"]}{RESET} {CYAN}via {data["route"]}{RESET}'
                )
            elif data["status"] == "Received":
                print(
                    f'{count} {data["name"]} {GREEN}Received {data["ip"]}{RESET} {CYAN}via {data["route"]}{RESET}'
                )



def run_scan(data, feed_type, args):
    """scan feed file"""

    if feed_type == "mcast":
        if args.direct:
            data = {"multicast": {"direct": {"test": args.direct}}}

        run_mcast(data)

    elif feed_type == "tcp":
        run_tcp(data, args)
    else:
        run_mcast(data)
        run_tcp(data, args)
