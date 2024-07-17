from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import RemoteController, Node
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info


class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class CustomTopo(Topo):
    def build(self, **_opts):
        # Add switches
        s1 = self.addSwitch('s1')  # Left switch
        s3 = self.addSwitch('s3')  # Middle switch
        s2 = self.addSwitch('s2')  # Rightmost switch

        # Add router
        router = self.addHost('router', cls=LinuxRouter)

        # Add links between switches
        self.addLink(s1, s3, intfName1='br1-trunk')
        self.addLink(s3, s2, intfName1='br2-trunk')
        self.addLink(router, s3, intfName1='router-eth0.100')
        self.addLink(router, s3, intfName1='router-eth0.200')

        # Add hosts
        h1 = self.addHost('h1', ip='192.168.100.2/24', defaultRoute='via 192.168.100.1')
        h2 = self.addHost('h2', ip='192.168.200.2/24', defaultRoute='via 192.168.200.1')
        h3 = self.addHost('h3', ip='192.168.100.3/24', defaultRoute='via 192.168.100.1')
        h4 = self.addHost('h4', ip='192.168.200.3/24', defaultRoute='via 192.168.200.1')

        # Add links between hosts and switches with VLANs
        self.addLink(h1, s1, intfName1='br1-eth1')
        self.addLink(h2, s1, intfName1='br1-eth2')
        self.addLink(h3, s2, intfName1='br2-eth3')
        self.addLink(h4, s2, intfName1='br2-eth4')

        # Configure trunk behaviour
        s1.cmd('ovs-vsctl set Port br1-trunk tag=[]')
        s1.cmd('ovs-vsctl set Port br2-trunk tag=[]')
        s2.cmd('ovs-vsctl set Port br2-eth3 tag=[]')
        s2.cmd('ovs-vsctl set Port br2-eth4 tag=[]')


def run():
    topo = CustomTopo()
    net = Mininet(topo=topo, controller=None, link=TCLink)
    net.addController(RemoteController('c0', ip='172.17.0.2'))

    net.start()

    # Configure router with sub-interfaces for VLANs
    router = net.get('router')
    router.cmd('ip link add link router-eth0 name router-eth0.100 type vlan id 100')
    router.cmd('ip link add link router-eth0 name router-eth0.200 type vlan id 200')
    router.cmd('ifconfig router-eth0.100 up')
    router.cmd('ifconfig router-eth0.200 up')
    router.cmd('ifconfig router-eth0.100 192.168.100.1/24')
    router.cmd('ifconfig router-eth0.200 192.168.200.1/24')

    # Add routing for reaching networks that aren't directly connected
    info(router.cmd("ip route add 192.168.100.1/24 dev router-eth0.100"))
    info(router.cmd("ip route add 192.168.200.1/24 dev router-eth0.200"))

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
