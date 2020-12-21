# Muffin
![Muffin](muffin.png)

Muffin is a connectivity testing tool designed primarily for Market Data testing but can be used for any multicast or TCP testing

Muffin can test TCP and Multicast connections

I created this module because I need a quick way to test basic market data connectivity health on my physical servers by defining easy to read YAML connectivity files. 

Muffin can show you basic connectivity status for your multicast groups and TCP IPs and ports, as well as few other features described below.

Here is a sample scan of my market data feeds:

Sample result of scanning a market data config YAML

<img src="screenshot.png" width="553">



---

## Requirements

- Linux OS (Tested on Centos 7 x64 server but should work with any modern Linux OS)
- Python minimum version 3.6 (may work with lower Python3 versions, need to test)

---

## Installation 

clone this repository

    cd /opt
    git clone git@github.com:perfecto25/muffin.git

create virtual environment
    
    cd muffin
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements
    

---


## Configuration

open config.py and update your preferences

- feed_files = path to your YAML feed
- mc_timeout = multicast timeout in seconds
- tcp_timeout = tcp timeout in seconds
- record_file = json file which records your inbound connections (optional)
- hosts = on each host where you run Muffin, update the Solarflare or interface IPs which you use to bind to multicast groups. (this can also be done directly in the feed YAML using "iface", see **feeds/mktdata.yaml**, line 23)

--- 

## Usage

1. define a connection file in feeds/file.yaml (see sample in **feeds/mktdata.yaml**)
1. open config.py and update *feed_file* variable to point to your file (can also pass this as command line flag, see below)
1. make sure config.py has IPs of your Solarflare or market data network interfaces (you can also define these in feed files directly, see Configuration section). Muffin uses these IPs to bind to Multicast groups

    ```
    hosts = { 
        'server1': ['192.168.18.10', '192.168.18.20'],
        'server2': ['192.168.18.11', '192.168.18.21'],
    }
    ```
1. run the scan

run 

    ./scan.py
    

    
## Additional command line flags

    # update config.py 'feed_files' variable with location of your YAML feed files
    
    ./scan.py   (this will scan both Mcast and TCP connections based on feed files defined in config.py)
    
    ./scan.py -t tcp   (will scan TCP only)
    
    ./scan.py -t mcast  (will scan Multicast only)
    
    ./scan.py -f /path/to/yaml   (will scan specific YAML feed file, ignoring the config.py setting)
    
    ./scan.py -c (will scan and output CSV result)
---   
   
## To convert an XML file to YAML

Muffin can also convert a Market data XML file into a YAML

open convert.py, it currently has conversion functions for CME and ICE market data formats.

at bottom, uncomment the Market type you want to convert, then run script,

    # converting CME XML file to YAML
    
    ./convert.py /path/to/cme_file.xml
    
for example, this ICE XML connectivity file can be converted to a feed YAML

```
<group name="ICE Endex Options">
    <top10pl>
        <live ip="233.156.208.116" port="20116" />
        <snapshot ip="233.156.208.117" port="20117" />
    </top10pl>
    <topOfBook>
        <live ip="233.156.208.104" port="20104" />
        <snapshot ip="233.156.208.105" port="20105" />
    </topOfBook>
</group>
```

convered to YAML

```
multicast:
  ICE Endex Options:
    top10pl-live:
      ip: 233.156.208.116
      port: 20116
    top10pl-snapshot:
      ip: 233.156.208.117
      port: 20117
    topOfBook-live:
      ip: 233.156.208.104
      port: 20104
    topOfBook-snapshot:
      ip: 233.156.208.105
      port: 20105
```

    


