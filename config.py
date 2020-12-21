import socket

### MUFFIN CONFIG 

# check multiple feed files
feed_files = [
    'feeds/mktdata.yaml',
]

# Multicast timeout in seconds 
mc_timeout = 30

# TCP connection timeout in seconds
tcp_timeout = 3


# interfaces to bind to
hosts = { 
    'server1': ['192.168.18.10', '192.168.18.20'],
    'server2': ['192.168.18.11', '192.168.18.21'],
}

# Terminal Colors
class txt: 
    reset='\033[0m'
    bold='\033[01m'
    disable='\033[02m'
    underline='\033[04m'
    reverse='\033[07m'
    strikethrough='\033[09m'
    invisible='\033[08m'
    class fg: 
        black='\033[30m'
        red='\033[31m'
        green='\033[32m'
        orange='\033[33m'
        blue='\033[34m'
        purple='\033[35m'
        cyan='\033[36m'
        white='\033[37m'
        lightgrey='\033[37m'
        darkgrey='\033[90m'
        lightred='\033[91m'
        lightgreen='\033[92m'
        yellow='\033[93m'
        lightblue='\033[94m'
        pink='\033[95m'
        lightcyan='\033[96m'
    class bg: 
        black='\033[35m'
        red='\033[41m'
        green='\033[42m'
        orange='\033[43m'
        blue='\033[44m'
        purple='\033[45m'
        cyan='\033[46m'
        lightgrey='\033[47m'
        white='\033[007m'

RED = f'{txt.bg.black}{txt.bold}{txt.fg.red}'
GREEN = f'{txt.fg.green}'
CYAN = f'{txt.fg.cyan}'
YELLOW = f'{txt.fg.yellow}'
WHITE = f'{txt.fg.white}'
PURPLE = f'{txt.bg.black}{txt.bold}{txt.fg.purple}'
ORANGE = f'{txt.bg.black}{txt.bold}{txt.fg.orange}'
RESET = f'{txt.reset}'

## check Solarflare ifaces
try:
    interfaces = hosts[socket.gethostname()]
except KeyError:
    print(f'{RED} Cant find interfaces for this host{RESET}')
    interfaces = ['127.0.0.1']