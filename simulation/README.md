# SDN Packet Logger

A comprehensive Software Defined Networking (SDN) solution for real-time packet capture and header analysis.

## Architecture
- **Controller**: Python-based Ryu application using OpenFlow 1.3.
- **Simulation**: Mininet topology (1 Switch, 3 Hosts).

## Prerequisites
- Linux Environment (WSL2, Ubuntu, etc.)
- Python 3.8+
- Ryu SDN Framework: `pip install ryu`
- Mininet: `sudo apt install mininet`

## Installation & Running

### 1. Start the Controller
Open a terminal and run:
```bash
# Start Ryu Controller
ryu-manager controller/packet_logger.py
```

### 2. Start the Simulation
Open a terminal with root privileges:
```bash
sudo python simulation/topology.py
```

### 3. Generate Traffic
In the Mininet CLI:
```bash
mininet> h1 ping h2
mininet> h1 curl h2
```

## Features
- **Header Extraction**: Full Ethernet, IPv4/v6, ARP, TCP, UDP, and ICMP header parsing.
- **Protocol Identification**: Automatic classification of traffic types.
- **History Management**: Stores the last 1000 packets in `logs/packets.json` for audit and analysis.
