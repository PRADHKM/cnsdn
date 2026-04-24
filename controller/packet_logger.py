from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from os_ken.ofproto import ofproto_v1_3
from os_ken.lib.packet import packet, ethernet, arp, ipv4, tcp, udp, icmp
import json
import os
import datetime

class PacketLogger(app_manager.OSKenApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(PacketLogger, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.log_file = 'logs/packets.json'
        
        # Initialize log file if not exists
        if not os.path.exists('logs'):
            os.makedirs('logs')
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Install table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if not eth:
            return

        dst = eth.dst
        src = eth.src
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        # Log packet headers
        self.log_packet(dpid, in_port, pkt)

        # Learning Switch Logic
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # Install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    def log_packet(self, dpid, in_port, pkt):
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        arp_pkt = pkt.get_protocol(arp.arp)
        ipv4_pkt = pkt.get_protocol(ipv4.ipv4)
        tcp_pkt = pkt.get_protocol(tcp.tcp)
        udp_pkt = pkt.get_protocol(udp.udp)
        icmp_pkt = pkt.get_protocol(icmp.icmp)

        packet_info = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "switch_id": dpid,
            "in_port": in_port,
            "src_mac": eth_pkt.src,
            "dst_mac": eth_pkt.dst,
            "eth_type": eth_pkt.ethertype,
            "protocol": "Unknown",
            "src_ip": "N/A",
            "dst_ip": "N/A",
            "src_port": "N/A",
            "dst_port": "N/A"
        }

        if arp_pkt:
            packet_info["protocol"] = "ARP"
            packet_info["src_ip"] = arp_pkt.src_ip
            packet_info["dst_ip"] = arp_pkt.dst_ip
        elif ipv4_pkt:
            packet_info["src_ip"] = ipv4_pkt.src
            packet_info["dst_ip"] = ipv4_pkt.dst
            if tcp_pkt:
                packet_info["protocol"] = "TCP"
                packet_info["src_port"] = tcp_pkt.src_port
                packet_info["dst_port"] = tcp_pkt.dst_port
            elif udp_pkt:
                packet_info["protocol"] = "UDP"
                packet_info["src_port"] = udp_pkt.src_port
                packet_info["dst_port"] = udp_pkt.dst_port
            elif icmp_pkt:
                packet_info["protocol"] = "ICMP"
            else:
                packet_info["protocol"] = "IPv4"

        # Append to log file
        try:
            with open(self.log_file, 'r+') as f:
                logs = json.load(f)
                logs.append(packet_info)
                # Keep only last 1000 packets for performance
                if len(logs) > 1000:
                    logs = logs[-1000:]
                f.seek(0)
                json.dump(logs, f, indent=2)
                f.truncate()
        except Exception as e:
            self.logger.error(f"Error logging packet: {e}")
