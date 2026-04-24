from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class SimpleStar(Topo):
    "Simple star topology with 3 hosts and 1 switch"
    def build(self):
        switch = self.addSwitch('s1')
        for h in range(3):
            host = self.addHost('h%s' % (h + 1), mac='00:00:00:00:00:0%s' % (h + 1))
            self.addLink(host, switch)

def run():
    topo = SimpleStar()
    # Connect to the remote controller (our packet_logger.py)
    net = Mininet(topo=topo,
                   controller=lambda name: RemoteController(name, ip='127.0.0.1'),
                   switch=OVSSwitch,
                   autoSetMacs=True)
    
    info('*** Starting network\n')
    net.start()
    
    info('*** Running CLI\n')
    CLI(net)
    
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
