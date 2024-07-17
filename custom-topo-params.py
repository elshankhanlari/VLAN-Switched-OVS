from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import RemoteController, Node
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info
import sys
from sys import argv


class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class ParametricTopo(Topo):
    def build(self, num_switches=3, hosts_per_switch=2):
        switches = []
        # Create switches
        for i in range(num_switches):
            switch = self.addSwitch(f's{i + 1}')
            switches.append(switch)

        # Create router
        router = self.addHost('router', cls=LinuxRouter)

        # Connect switches linearly
        for i in range(len(switches) - 1):
            self.addLink(switches[i], switches[i + 1])

        # Connect router to the middle switch
        middle_switch = switches[num_switches // 2]
        self.addLink(router, middle_switch)

        # Create hosts and connect them to the appropriate switches with VLANs
        for i in range(hosts_per_switch):
            h1 = self.addHost(f'h{1 + i * 2}', ip=f'192.168.100.{2 + i * 2}/24', defaultRoute='via 192.168.100.1')
            h2 = self.addHost(f'h{2 + i * 2}', ip=f'192.168.200.{2 + i * 2}/24', defaultRoute='via 192.168.200.1')
            self.addLink(h1, switches[0], params1={'vlan': 100})
            self.addLink(h2, switches[0], params1={'vlan': 200})
            h3 = self.addHost(f'h{3 + i * 2}', ip=f'192.168.100.{3 + i * 2}/24', defaultRoute='via 192.168.100.1')
            h4 = self.addHost(f'h{4 + i * 2}', ip=f'192.168.200.{3 + i * 2}/24', defaultRoute='via 192.168.200.1')
            self.addLink(h3, switches[-1], params1={'vlan': 100})
            self.addLink(h4, switches[-1], params1={'vlan': 200})


def run(num_switches=3, hosts_per_switch=2):
    topo = ParametricTopo(num_switches=num_switches, hosts_per_switch=hosts_per_switch)
    net = Mininet(topo=topo, controller=None, link=TCLink)
    net.addController(RemoteController('c0', ip='172.17.0.2'))

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

    # Default values
    num_switches = 3
    hosts_per_switch = 2
    run(num_switches, hosts_per_switch)
