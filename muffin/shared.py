import os
import sys
import socket
import yaml
import psutil
import socket
from pathlib import Path

hostname = socket.gethostname()
base_dir = Path(__file__).resolve().parent.parent

# Terminal Colors
class txt:
    reset = "\033[0m"
    bold = "\033[01m"
    disable = "\033[02m"
    underline = "\033[04m"
    reverse = "\033[07m"
    strikethrough = "\033[09m"
    invisible = "\033[08m"

    class fg:
        black = "\033[30m"
        red = "\033[31m"
        green = "\033[32m"
        orange = "\033[33m"
        blue = "\033[34m"
        purple = "\033[35m"
        cyan = "\033[36m"
        white = "\033[37m"
        lightgrey = "\033[37m"
        darkgrey = "\033[90m"
        lightred = "\033[91m"
        lightgreen = "\033[92m"
        yellow = "\033[93m"
        lightblue = "\033[94m"
        pink = "\033[95m"
        lightcyan = "\033[96m"

    class bg:
        black = "\033[35m"
        red = "\033[41m"
        green = "\033[42m"
        orange = "\033[43m"
        blue = "\033[44m"
        purple = "\033[45m"
        cyan = "\033[46m"
        lightgrey = "\033[47m"
        white = "\033[007m"

RED = f"{txt.bg.black}{txt.bold}{txt.fg.red}"
GREEN = f"{txt.fg.green}"
CYAN = f"{txt.fg.cyan}"
YELLOW = f"{txt.fg.yellow}"
WHITE = f"{txt.fg.white}{txt.bold}"
PURPLE = f"{txt.bg.black}{txt.bold}{txt.fg.purple}"
ORANGE = f"{txt.bg.black}{txt.bold}{txt.fg.orange}"
RESET = f"{txt.reset}"



def _get_cfg():
    """ returns config YAML data as dict """
    with open(f"{base_dir}/config.yaml") as cfgfile:
        try:
            cfg = yaml.load(cfgfile, Loader=yaml.FullLoader)
        except yaml.YAMLError as e:
            print(f"{RED}{str(e)}{RESET}")
            sys.exit()
    return cfg

cfg = _get_cfg()

def _get_ifaces(iface_type=None):
    """ returns IPs of solarflare ifaces on this host """
    ret = []
    ifaces = cfg["sf_ifaces"]

    for name, addrs in psutil.net_if_addrs().items():
        if name in ifaces:
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ret.append(addr.address)
    return ret


def _check_file(file):
    """ check if file exists """
    # if still not present, error out
    if not os.path.exists(file):
        print(f"{RED} File does not exist: {file} {RESET}")
        sys.exit()


def _get_feeds(env):
    """ returns a list of market data yaml feeds to check """
    feed_files = []

    if env:
        for feed in os.listdir(cfg['hosts'][hostname]['feeds'][env]):
            if not feed:
                print(f"{RED} No feed files in config.yaml for this host{RESET}")
                sys.exit()
            feed_files.append(cfg['hosts'][hostname]['feeds'][env]+"/"+feed)
    else:
        for env in cfg["hosts"][hostname]['feeds']:
            for feed in os.listdir(cfg['hosts'][hostname]['feeds'][env]):
                if not feed:
                    print(f"{RED} No feed files in config.yaml for this host{RESET}")
                    sys.exit()
                feed_files.append(cfg['hosts'][hostname]['feeds'][env]+"/"+feed)
    return feed_files


