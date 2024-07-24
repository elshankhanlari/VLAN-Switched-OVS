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
    def build(self, num_switches=3, **_opts):
        if num_switches < 3:
            raise ValueError("The number of switches must be at least 3.")

        # Add switches
        switches = [self.addSwitch(f's{i + 1}') for i in range(num_switches)]

        # Add router
        router = self.addHost('router', cls=LinuxRouter)

        # Add links between switches
        for i in range(num_switches - 1):
            self.addLink(switches[i], switches[i + 1])

        # Connect middle switch to the router
        middle_switch_index = num_switches // 2
        middle_switch = switches[middle_switch_index]
        self.addLink(router, middle_switch, intfName1='router-eth0.100')
        self.addLink(router, middle_switch, intfName1='router-eth0.200')

        # Add hosts and assign them to VLANs
        for i in range(1, middle_switch_index + 1):
            vlan_id = 100 if i % 2 == 1 else 200
            host1 = self.addHost(f'h{2*i}', ip=f'192.168.{vlan_id}.{i + 1}/24', defaultRoute=f'via 192.168.{vlan_id}.1')
            host2 = self.addHost(f'h{2*i+1}', ip=f'192.168.{vlan_id}.{i + 2}/24', defaultRoute=f'via 192.168.{vlan_id}.1')
            self.addLink(host1, switches[i - 1], intfName1=f'br{i}-eth1')
            self.addLink(host2, switches[i - 1], intfName1=f'br{i}-eth2')


def run(num_switches=3):
    topo = CustomTopo(num_switches=num_switches)
    net = Mininet(topo=topo, controller=None, link=TCLink)
    net.addController(RemoteController('c0', ip='172.17.0.2'))

    net.start()

    middle_switch_index = num_switches // 2
    middle_switch = net.get(f's{middle_switch_index + 1}')

    # Configure trunk behaviour
    for i in range(num_switches):
        if i < num_switches - 1:
            net.get(f's{i + 1}').cmd(f'ovs-vsctl set Port s{i + 1}-eth{i + 2} tag=[]')

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
    num_switches = 3  # Default number of switches, change this value as needed
    run(num_switches)
