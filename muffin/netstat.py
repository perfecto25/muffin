#!venv/bin/python3
from __future__ import absolute_import, print_function
from dictor import dictor
import sys
import psutil
import os
import socket
import json
from json.decoder import JSONDecodeError
from io import UnsupportedOperation
import yaml
from collections import OrderedDict
    
def netstat():
    ''' gets ordered dict of all active tcp conns '''
    
    connections = psutil.net_connections(kind='tcp')
    
    active = {}
    
    for conn in connections:
        if conn.status == 'LISTEN':
            ip = conn.laddr[0]
            port = conn.laddr[1]

            if not port in active.keys():
                active[port] = []
            
            for c in connections:
                if c.status == 'ESTABLISHED' and c.laddr[1] == port:
                    client_ip = c.raddr[0]
                    bind_port = c.raddr[1]
                    if client_ip == '127.0.0.1':
                        continue
                    active[port].append(client_ip)

    # remove duplicate IPs
    for k,v in active.items():
        active[k] = list(set(v))
        
    # remove null values
    empty_keys = [k for k,v in active.items() if not v]
    for k in empty_keys: del active[k]
    od = OrderedDict(sorted(active.items(),key=lambda x:x[0]))
    return od



        