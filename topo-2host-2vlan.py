from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import OVSSwitch, RemoteController, CPULimitedHost
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class VLANTopology(Topo):
    def build(self):
        # Create switches
        s1 = self.addSwitch('s1', protocols='OpenFlow13')
        s2 = self.addSwitch('s2', protocols='OpenFlow13')

        # Create hosts for VLAN 10
        h1 = self.addHost('h1', ip='192.168.10.1/24')
        h2 = self.addHost('h2', ip='192.168.10.2/24')

        # Create hosts for VLAN 20
        h3 = self.addHost('h3', ip='192.168.20.1/24')
        h4 = self.addHost('h4', ip='192.168.20.2/24')

        # Add links between hosts and switches
        self.addLink(h1, s1, port1=1, port2=1)
        self.addLink(h2, s1, port1=1, port2=2)
        self.addLink(h3, s2, port1=1, port2=1)
        self.addLink(h4, s2, port1=1, port2=2)

        # Add link between the switches
        self.addLink(s1, s2, port1=3, port2=3)

def configure_vlans(net):
    s1 = net.get('s1')
    s2 = net.get('s2')
    
    s1.cmd('ovs-vsctl set port s1-eth1 tag=10')
    s1.cmd('ovs-vsctl set port s1-eth2 tag=10')
    s2.cmd('ovs-vsctl set port s2-eth1 tag=20')
    s2.cmd('ovs-vsctl set port s2-eth2 tag=20')

if __name__ == '__main__':
    setLogLevel('info')
    
    # Create and start the network
    topo = VLANTopology()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=RemoteController, host=CPULimitedHost)
    
    net.start()
    
    # Configure VLANs
    configure_vlans(net)
    
    # Test network connectivity
    print("Testing network connectivity")
    net.pingAll()
    
    # Test bandwidth between hosts in the same VLAN
    print("Testing bandwidth within VLAN 10")
    h1, h2 = net.get('h1', 'h2')
    net.iperf((h1, h2))
    
    print("Testing bandwidth within VLAN 20")
    h3, h4 = net.get('h3', 'h4')
    net.iperf((h3, h4))
    
    # Open Mininet CLI
    CLI(net)
    
    # Stop the network
    net.stop()
