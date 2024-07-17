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

        # Add router
        router = self.addHost('r1', cls=LinuxRouter, ip=['192.168.100.1/24',
                                                         '192.168.200.1/24'])

        # Add switches
        s1 = self.addSwitch('s1')  # Left switch
        s3 = self.addSwitch('s3')  # Middle switch
        s2 = self.addSwitch('s2')  # Rightmost switch

        # Add links between switches and router
        self.addLink(s1, s3)
        self.addLink(s3, s2)
        self.addLink(router, s3)

        # Add hosts
        h1 = self.addHost('h1', ip='192.168.100.2/24', defaultRoute='via 192.168.100.1')
        h2 = self.addHost('h2', ip='192.168.200.2/24', defaultRoute='via 192.168.200.1')
        h3 = self.addHost('h3', ip='192.168.100.3/24', defaultRoute='via 192.168.100.1')
        h4 = self.addHost('h4', ip='192.168.200.3/24', defaultRoute='via 192.168.200.1')

        # Add host-switch links
        self.addLink(h1,
                     s1,
                     intfName2='eth1-s1',
                     params2={'ip': '192.168.100.2/24'})

        self.addLink(h2,
                     s1,
                     intfName2='eth2-s1',
                     params2={'ip': '192.168.200.2/24'})

        self.addLink(h3,
                     s2,
                     intfName2='eth3-s2',
                     params2={'ip': '192.168.100.3/24'})

        self.addLink(h4,
                     s2,
                     intfName2='eth4-s2',
                     params2={'ip': '192.168.200.3/24'})


def run():
    topo = CustomTopo()
    net = Mininet(topo=topo, controller=None)
    net.addController(RemoteController('c0', ip='172.17.0.2'))

    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
