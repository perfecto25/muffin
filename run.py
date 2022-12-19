#!/opt/muffin/venv/bin/python3
import yaml
from dictor import dictor
import sys
import argparse
import textwrap
from muffin import run_scan
from muffin.shared import RED, GREEN, WHITE, RESET, _check_file, _get_feeds

def _scan(feed_file, feed_type, args):
    with open(feed_file, "r") as file:
        try:
            data = yaml.load(file, Loader=yaml.FullLoader)
        except yaml.YAMLError as e:
            print(f"{RED}{str(e)}{RESET}")
            sys.exit()
    print(f"\n{WHITE}Reading file: {feed_file} {RESET}")
    run_scan(data, feed_type, args)

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent(
        """
    Muffin - TCP and Multicast connection scanner
    > muffin                                    # scans feed files defined in /etc/muffin/config.yaml
    > muffin -f /etc/muffin/feeds/myfeed.yaml   # scans a specific feed file
    > muffin -t tcp                             # only scan TCP connections
    > muffin -t mcast                # only scan Multicast connections
    > muffin -n                      # show active inbound connections (netstat)
    > muffin -n -r                   # show active inbound connections and record to JSON file
    > muffin -n -j                   # show active inbound connections as JSON
    > muffin -c /path/to/config      # use a custom config file
    > muffin -d 233.150.1.200:21000  # test mcast connectivity directly without a YAML
    > muffin -e uat                  # test YAML feeds for specific environment
    """
    ),
)

parser.add_argument("-f", "--feed", help="scan a specific feed file path")
parser.add_argument("-e", "--env", help="scan a specific environment feed file")
parser.add_argument("-t", "--type", help='protocol type "tcp, udp, mcast", default="tcp, udp, and mcast"')
parser.add_argument("-d", "--direct", help="test multicast directly by providing IP and Port")
parser.add_argument("-j", "--json", help='output in JSON format, default="False"', action="store_true")
parser.add_argument("-c", "--config", help='path to config file')
parser.add_argument('--version', action='version', version='muffin 1.0.3')

if __name__ == "__main__":
    args = parser.parse_args()

    if args.direct:
        run_scan(None, "mcast", args)
        sys.exit()

    if not args.type:
        args.type = "all"

    # single feed file from cmd line
    if args.feed:
        _check_file(args.feed)
        _scan(args.feed, args.type, args)
    else:
        # read feed files from config file
        feed_files = _get_feeds(args.env)

        for feed in feed_files:
            _check_file(feed)
            _scan(feed, args.type, args)

    if not args.record and not args.json:
        print(f"\n\n{GREEN}---- End of Scan ----" + RESET)
