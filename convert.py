#!venv/bin/python3
from __future__ import absolute_import, print_function
import yaml
from dictor import dictor
import socket
import struct
import sys
import json
from json.decoder import JSONDecodeError
from io import UnsupportedOperation
import os
import pprint
import xmltodict
import configparser
from collections import OrderedDict
from config import RED, WHITE, RESET

### Converts XML to YAML

if len(sys.argv) < 3:
    print(f"{RED} Provide type of market to convert and path to file {RESET}")
    print(f"{WHITE}ie: ./convert.py ice ice.xml {RESET}")
    sys.exit()
    
market = sys.argv[1]
feed = sys.argv[2]

pp = pprint.PrettyPrinter(indent=2)
output = {}
output["multicast"] = {}
output["tcp"] = {}


if not os.path.exists(feed):
    print(f"{RED} Feed file does not exist: {feed} {RESET}")
    sys.exit()    
    
def cme_xml(feed):
    """ parse CME XML config and generate YAML """
    
    with open(feed) as file:
        data = xmltodict.parse(file.read())
        
    jd = json.dumps(data)
    jd = json.loads(jd)
    
    for c in dictor(jd, "configuration.channel"):
    
        group = dictor(c, "@label")
        conns = dictor(c, "connections.connection")
        
        for conn in conns:
            fid = dictor(conn, "@id")
            feed = dictor(conn, "feed")
            ip = dictor(conn, "ip")
            port = dictor(conn, "port")
            protocol = dictor(conn, "protocol")
            desc = dictor(conn, "type.#text")
    
            pmap = { "TCP/IP": "tcp", "UDP/IP": "multicast", "Multicast": "multicast" }
            protoc = pmap[protocol]  
                
            if not dictor(output, f"{protoc}"):
                output[protoc] = {}
                
            if not dictor(output, f"{protoc}.{group}"):
                output[protoc][group] = {}
            
            if type(ip) is list:
                for ipaddr in ip:
                    idx = str(ip.index(ip))
                    output[protoc][group][f"{desc} ({feed}) [{fid}] {idx}"] = {}
                    output[protoc][group][f"{desc} ({feed}) [{fid}] {idx}"]["ip"] = ipaddr
                    output[protoc][group][f"{desc} ({feed}) [{fid}] {idx}"]["port"] = int(port)              
            else:
                output[protoc][group][f"{desc} ({feed}) [{fid}]"] = {}
                output[protoc][group][f"{desc} ({feed}) [{fid}]"]["ip"] = ip
                output[protoc][group][f"{desc} ({feed}) [{fid}]"]["port"] = int(port)
                
    return yaml.dump(output, default_flow_style=False)
    
def ice_xml(feed):
    """ parse ICE xml and turn into YAML """
    
    with open(feed) as file:
        data = xmltodict.parse(file.read())
        
    jd = json.dumps(data)
    jd = json.loads(jd)
    
    groups = dictor(data, 'connectivityConfiguration.multicast.group', pretty=False)
    for group in groups:
        od = OrderedDict(sorted(group.items(),key=lambda x:x[0]))
        group_name = od['@name']
        output["multicast"][group_name] = {}
        od.pop('@name')
        
        for subgroup in od:
 
            if isinstance(od[subgroup], list):
                for feed in od[subgroup]:
                    #print(feed)
                    for k,v in feed.items():
                        if k == 'live' or k == 'snapshot':
                            if not dictor(output, f"multicast.{group_name}.{subgroup}-{k}"):
                                output["multicast"][group_name][subgroup+"-"+k] = {}
                            ip = dictor(v, '@ip', checknone=True)
                            port = dictor(v, '@port', checknone=True)
                            output["multicast"][group_name][subgroup+"-"+k]["ip"] = ip
                            output["multicast"][group_name][subgroup+"-"+k]["port"] = int(port)
            else:
                for k,v in od[subgroup].items():
                    if k == 'live' or k == 'snapshot':
                        if not dictor(output, f"multicast.{group_name}.{subgroup}-{k}"):
                            output["multicast"][group_name][subgroup+"-"+k] = {}
                        ip = dictor(v, '@ip', checknone=True)
                        port = dictor(v, '@port', checknone=True)
                        output["multicast"][group_name][subgroup+"-"+k]["ip"] = ip
                        output["multicast"][group_name][subgroup+"-"+k]["port"] = int(port)
    return yaml.dump(output, default_flow_style=False)


if __name__ == "__main__":
    
    if market == 'cme':
        print(cme_xml(feed))

    if market == 'ice':
        print(ice_xml(feed))

