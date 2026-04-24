import time

class Packet:
    def __init__(self, src, dst, protocol, payload):
        self.src = src
        self.dst = dst
        self.protocol = protocol
        self.payload = payload

class Host:
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip
        self.connected_switch = None

    def send(self, dst_ip, protocol, payload=""):
        print(f"{self.name} is sending {protocol} packet to {dst_ip}...", flush=True)
        packet = Packet(self.ip, dst_ip, protocol, payload)
        if self.connected_switch:
            return self.connected_switch.handle_packet(packet)
        return False

class Switch:
    def __init__(self, name):
        self.name = name
        self.flow_table = set()
        self.ports = {}

    def add_port(self, host):
        self.ports[host.ip] = host
        host.connected_switch = self

    def handle_packet(self, packet):
        flow = (packet.src, packet.dst, packet.protocol)
        if flow not in self.flow_table:
            print(f"[Controller] INFO: Handling Flow table MISS for new flow from {packet.src} to {packet.dst} ({packet.protocol})", flush=True)
            self.flow_table.add(flow)
            return True # Miss
        else:
            return False # Hit (silent to match screenshot style)

def run_simulation():
    # Initialize components
    s1 = Switch("s1")
    h1 = Host("h1", "10.0.0.1")
    h2 = Host("h2", "10.0.0.2")
    h3 = Host("h3", "10.0.0.3")
    
    s1.add_port(h1)
    s1.add_port(h2)
    s1.add_port(h3)

    print("=== SDN Structured Packet Scanner Started ===", flush=True)
    print("Press Ctrl+C to stop scanning...\n", flush=True)
    
    # Define a logical sequence of traffic
    traffic_scenarios = [
        (h3, h1, "UDP"),
        (h3, h1, "UDP"),  # Repeat to show HIT (silent)
        (h3, h2, "UDP"),
        (h3, h1, "TCP"),
        (h1, h2, "ICMP"),
        (h2, h3, "TCP"),
        (h1, h3, "UDP")
    ]
    
    try:
        while True:
            for src, dst, proto in traffic_scenarios:
                src.send(dst.ip, proto)
                time.sleep(1.5) # Consistent delay for screenshot taking
                
    except KeyboardInterrupt:
        print("\n\n=== Scanning Halted by User ===", flush=True)

if __name__ == '__main__':
    run_simulation()
