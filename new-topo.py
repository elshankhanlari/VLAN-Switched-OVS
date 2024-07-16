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
        self.addLink(s1, s3)
        self.addLink(s3, s2)
        self.addLink(router, s3)

        # Add hosts
        h1 = self.addHost('h1', ip='192.168.100.2/24', defaultRoute='via 192.168.100.1')
        h2 = self.addHost('h2', ip='192.168.200.2/24', defaultRoute='via 192.168.200.1')
        h3 = self.addHost('h3', ip='192.168.100.3/24', defaultRoute='via 192.168.100.1')
        h4 = self.addHost('h4', ip='192.168.200.3/24', defaultRoute='via 192.168.200.1')

        # Add links between hosts and switches with VLANs
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)

        # Create OVS bridge for each switch and connect them
        self.addLink(s1, router, intfName2='router-eth0', params2={'ip': '192.168.100.1/24'})
        self.addLink(s2, router, intfName2='router-eth1', params2={'ip': '192.168.200.1/24'})

        # Tag VLANs on router interfaces using OVS commands
        router.cmd('ovs-vsctl add-port router-eth0 router-eth0.100 tag=100')
        router.cmd('ifconfig router-eth0.100 192.168.100.1/24')

        router.cmd('ovs-vsctl add-port router-eth1 router-eth1.200 tag=200')
        router.cmd('ifconfig router-eth1.200 192.168.200.1/24')


def run():
    topo = CustomTopo()
    net = Mininet(topo=topo, controller=None, link=TCLink)
    net.addController(RemoteController('c0', ip='172.17.0.2'))

    net.start()

    # Enable IP forwarding on the router
    router = net.get('router')
    router.cmd('sysctl net.ipv4.ip_forward=1')

    # Test connectivity
    net.get('h1').cmd('ping -c1 192.168.100.3')
    net.get('h1').cmd('ping -c1 192.168.200.3')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
