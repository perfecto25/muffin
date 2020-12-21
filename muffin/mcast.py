from __future__ import absolute_import, print_function
import yaml
from dictor import dictor
import socket
import struct
import sys
import os
from config import mc_timeout, interfaces, RED, GREEN, RESET

def mcast(ip, port, iface, feed, group, count, args):
    ''' connect multicast group connectivity for each solarflare iface '''
    port = int(port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((ip, port))
    except socket.error:
        print(f'{group} {feed} {RED} Invalid Group {ip}:{port} on {iface} {RESET}')
        return 1

    if iface is "":
        mreq = struct.pack('4sl', socket.inet_aton(ip), socket.INADDR_ANY)
    else:
        mreq = socket.inet_aton(ip) + socket.inet_aton(iface)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.settimeout(mc_timeout)
    
    i = 0
    while i<1:
        try:
            data, addr = sock.recvfrom(port)
        except socket.timeout:
            if args.csv:
                print(f'{count},mc,{group},{feed},{ip},{port},{iface},Timed out')
            else:
                print(f"{count} [mc] {group} {feed} {RED} Timed out {ip}:{port} on {iface} {RESET}")
            break
        else:
            if args.csv:
                print(f'{count},mc,{group},{feed},{ip},{port},{iface},Received')
            else:
                print(f"{count} [mc] {group} {feed} {GREEN} Received on {ip}:{port} on {iface} {RESET}")
        i += 1

