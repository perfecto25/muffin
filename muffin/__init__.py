#!venv/bin/python3
from __future__ import absolute_import, print_function
import yaml
from dictor import dictor
import socket
import struct
import sys
import os
from muffin.mcast import mcast
from muffin.tcp import tcp
from config import interfaces, mc_timeout, tcp_timeout, CYAN, RED, WHITE, GREEN, RESET

def run_mcast(data, args):
    
    ## MULTICAST
    if dictor(data, 'multicast'):
        print(f'\n{WHITE}Checking Multicast connectivity - timeout: {mc_timeout} sec{RESET}')
        count = 0
        
        for group in dictor(data, 'multicast'):
            for feed in (dictor(data, f'multicast.{group}')):
                ip = dictor(data, f'multicast.{group}.{feed}.ip', checknone=True)
                count += 1
            
                if dictor(data, f'multicast.{group}.{feed}.ports'):
                    ports = dictor(data, f'multicast.{group}.{feed}.ports').split(',')
                    ports = list(set(sorted(ports)))
                    ports = filter(None, ports)
                    for port in sorted(ports):
                        if type(port) is str: 
                            port = port.strip()
                            
                            iface = dictor(data, f'multicast.{group}.{feed}.iface')
                            if iface: 
                                mcast(ip, port, iface, feed, group, count, args)
                            else:
                                for iface in interfaces:
                                    mcast(ip, port, iface, feed, group, count, args)
                else:
                    port = dictor(data, f'multicast.{group}.{feed}.port')
                    
                    iface = dictor(data, f'multicast.{group}.{feed}.iface')
                    if iface:
                        mcast(ip, port, iface, feed, group, count, args)
                    else:
                        for iface in interfaces:
                            mcast(ip, port, iface, feed, group, count, args)
                   
def run_tcp(data, args):
    ## TCP
    if dictor(data, 'tcp'):
        print(f'\n\n{WHITE}Checking TCP connectivity - timeout: {tcp_timeout} sec{RESET}')
        count = 0
        for group in dictor(data, 'tcp'):
            for feed in (dictor(data, f'tcp.{group}')):                
                ip = dictor(data, f'tcp.{group}.{feed}.ip')
                count += 1
                
                # if multiple ports
                if dictor(data, f'tcp.{group}.{feed}.ports'):
                    ports = dictor(data, f'tcp.{group}.{feed}.ports')
                    
                    # comma separated list of ports, ie 1200,1201,1202
                    if ',' in ports:
                        ports = dictor(data, f'tcp.{group}.{feed}.ports').split(',')
                        ports = list(set(sorted(ports)))
                        
                    # range of ports, ie 1200-1205
                    if '-' in ports:
                        minval = ports.split('-')[0]
                        maxval = int(ports.split('-')[1])+1
                        ports = []
                        for p in range(int(minval), int(maxval)):
                            ports.append(p)
                                            
                    ports = filter(None, ports)

                    for port in sorted(ports):
                        if type(port) is str: 
                            port = port.strip()
                        tcp(ip, port, feed, group, count, args)
                else:
                    port = dictor(data, f'tcp.{group}.{feed}.port')
                    tcp(ip, port, feed, group, count, args)


def run_scan(data, feed_type, args):
    ''' parse MC yaml '''
    if feed_type == "mcast":
        run_mcast(data, args)
    elif feed_type == "tcp":
        run_tcp(data, args)
    else:
        run_mcast(data, args)
        run_tcp(data, args)
    
   

                    
   