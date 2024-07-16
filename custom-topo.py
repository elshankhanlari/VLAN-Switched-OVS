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
        self.addLink(h1, s1, params1={'vlan': 100})
        self.addLink(h2, s1, params1={'vlan': 200})
        self.addLink(h3, s2, params1={'vlan': 100})
        self.addLink(h4, s2, params1={'vlan': 200})


def run():
    topo = CustomTopo()
    net = Mininet(topo=topo, controller=None, link=TCLink)
    net.addController(RemoteController('c', ip='172.17.0.2'))

    # Configure router with two IP addresses for inter-VLAN routing
    router = net.get('router')
    router.cmd('ifconfig router-eth0 192.168.100.1/24')
    router.cmd('ifconfig router-eth0 add 192.168.200.1/24')

    net.start()

    # Add routing for reaching networks that aren't directly connected
    info(router.cmd("ip route add 192.168.200.0/24 dev router-eth0"))
    info(router.cmd("ip route add 192.168.100.0/24 dev router-eth0"))

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
