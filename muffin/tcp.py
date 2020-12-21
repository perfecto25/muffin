from __future__ import absolute_import, print_function
import yaml
from dictor import dictor
import socket
import struct
import sys
import os
import re
from .netstat import netstat
import psutil
from pyroute2 import IPRoute
from config import tcp_timeout, RED, GREEN, CYAN, ORANGE, PURPLE, RESET

def check_not_hostname(ip):
    ''' checks if IP is ipv4 and not a hostname '''
    regex = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    return regex.match(ip)
    
def get_route(ip):
    ''' returns the route gateway of an IP address '''

    route = None
    
    if check_not_hostname(ip):
        with IPRoute() as ipr:
            for rt in ipr.get_routes(family=socket.AF_INET, dst=ip):
                for r in dictor(rt, 'attrs'):
                    if r[0] == "RTA_GATEWAY":
                        route = r[1]
    if route:
        return route
    else: 
        return "N/A"

def tcp(ip, port, feed, group, count, args):
    ''' test TCP connectivity from host '''
    ## check if connection is already established, get ordered dict of all active netstat connections
    od = netstat()
    
    ## if IP is already connected on this host, skip to next IP
    if port in od:
        if ip in od[port]:            
            print(f'{count} [tcp] {group} {feed} {GREEN} Already connected to this host: {ip}:{port} {RESET}')
            return
    
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

    s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(tcp_timeout)
    result = s.connect_ex((ip_addr, int(port)))
    s.close()
    route = get_route(ip)
    
    # connection return code
    return_code = {
        '111': ['Refused', f'{RED}'],
        '11': ['Timeout', f'{ORANGE}'],
        '0': ['Received', f'{GREEN}']
    }

    status = dictor(return_code, f'{result}.0')
    color = dictor(return_code, f'{result}.1')
    
    if args.csv:
        print(f'tcp,{group},{feed},{ip},{port},{status}')
    else:
        print(f'{count} [tcp] {group} {feed} {color}{status} {ip}:{port}{RESET} {CYAN}via {route}{RESET}')    
   