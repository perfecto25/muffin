#!venv/bin/python3
from __future__ import absolute_import, print_function
import yaml
from dictor import dictor
import socket
import struct
import sys
import os
import argparse
import textwrap
from muffin import run_scan
from config import feed_files, CYAN, RED, WHITE, GREEN, RESET

def _check_file(feed_file):
    if not os.path.exists(feed_file):
        print(f'{RED} Feed connection file does not exist: {feed_file} {RESET}')
        sys.exit()

def _scan(feed_file, feed_type, args):
    with open(feed_file, "r") as file:
        try:
            data = yaml.load(file, Loader=yaml.FullLoader)
        except yaml.YAMLError as e:
            print(str(e))
            sys.exit()
            
        print(f'\n{WHITE}Reading file: {feed_file} {RESET}')
        run_scan(data, feed_type, args)

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''
    Muffin - Connection Scanner
    ./scan.py                        # scans feed files defined in config.py
    ./scan.py -f feeds/myfeed.yaml   # scans a specific feed file
    ./scan.py -t tcp                 # only scan TCP connections
    ./scan.py -t mcast               # only scan Multicast connections
    ./scan.py -f feed.yaml -c        # show connectivity as CSV
    '''))

parser.add_argument('-f', '--feed', help='scan a specific feed file path')
parser.add_argument('-t', '--type', help='protocol type "tcp, mcast", default="tcp and mcast"')
parser.add_argument('-c', '--csv', help='output in CSV format, default="False"', action='store_true')

if __name__ == "__main__":
    
    args = parser.parse_args()
    
    if not args.type:
        args.type = 'all'

    # single feed file from cmd line
    if args.feed:
        _check_file(args.feed)
        _scan(args.feed, args.type, args)
    else:
       
        # read feed files from config.py
        for feed_file in feed_files:
            _check_file(feed_file)
            _scan(feed_file, args.type, args)    

    
    print(f'\n\n{GREEN}---- End of Scan ----' + RESET)
