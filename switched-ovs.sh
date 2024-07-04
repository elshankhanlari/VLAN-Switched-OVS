#!bin/bash

echo "--- Create an OVS switch"
ovs-vsctl add-br br1
ovs-vsctl add-br br2
ovs-vsctl add-br br3

echo "--- Show OVS bridges"

ovs-vsctl show

echo "--- Activate the OVS switch named lab2-br1..."

ifconfig br1 up
ifconfig br2 up
ifconfig br3 up

echo "--- Add interface to the OVS..."

ovs-vsctl add-port br2 enp0s3

ovs-vsctl show

echo "--- Delete IP configuration of port enp0s3..."

ifconfig enp0s3 0

echo "--- Assign an IP to the bridge using DHCP local..."

dhclient br1 br2 br3

echo "--- Show the routing table..."
route -n

echo "Creating namespaces..."
ip netns add yellow1
ip netns add green1
ip netns add yellow2
ip netns add green2
ip netns add router
sleep 1

echo "Creating links..."
ip link add veth-yellow1 type veth peer name veth-yellow1-br
ip link add veth-green1 type veth peer name veth-green1-br
ip link add veth-yellow2 type veth peer name veth-yellow2-br
ip link add veth-green2 type veth peer name veth-green2-br
sleep 1

echo "Moving interfaces into the namespaces"
ip link set veth-yellow1 netns yellow1
ip link set veth-green1 netns green1
ip link set veth-yellow2 netns yellow2
ip link set veth-green2 netns green2
ip link set router-trunk netns router
sleep 1

echo "---> Attaching interfaces to ovs-switch"
ovs-vsctl add-port br1 veth-yellow1-br
ovs-vsctl add-port br1 veth-green1-br
ovs-vsctl add-port br2 veth-yellow2-br
ovs-vsctl add-port br2 veth-green2-br
sleep 1

echo "Configuring IP addresses..."
ip -n yellow1 addr add 192.168.100.2/24 dev veth-yellow1
ip -n green1 addr add 192.168.200.2/24 dev veth-green1
ip -n yellow2 addr add 192.168.100.3/24 dev veth-yellow2
ip -n green2 addr add 192.168.200.3/24 dev veth-green2
sleep 1

echo "--- Set VLAN access ports..."

ovs-vsctl set port veth-yellow1-br tag=100
ovs-vsctl set port veth-green1-br tag=200
ovs-vsctl set port veth-yellow2-br tag=100
ovs-vsctl set port veth-green2-br tag=200

echo "Turning up the interfaces within namespaces..."
ip -n yellow1 link set veth-yellow1 up
ip -n green1 link set veth-green1 up
ip -n yellow2 link set veth-yellow2 up
ip -n green2 link set veth-green2 up
ip -n green2 link set veth-green2 up
sleep 1

echo "Turning up the interfaces within default namespace..."
sudo ip link set veth-yellow1-br up
sudo ip link set veth-green1-br up
sudo ip link set veth-yellow2-br up
sudo ip link set veth-green2-br up
echo "--- OVS show ---"

ovs-vsctl show

echo "--- Creating link between switches..."
ip link add br1-trunk type veth peer name br1-b3-trunk
ip link add br2-trunk type veth peer name br2-br3-trunk
ip link add br3-router-trunk type veth peer name router-trunk
sleep 1

echo "--- Add trunk port to switches..."
ovs-vsctl add-port br1 br1-trunk
ovs-vsctl add-port br3 br1-b3-trunk
ovs-vsctl add-port br3 br2-b3-trunk
ovs-vsctl add-port br2 br2-trunk
ovs-vsctl add-port br3 br3-router-trunk
sleep 1

echo "--- Turning up trunk interfaces..."
sudo ip link set br1-trunk up
sudo ip link set br2-trunk up
sudo ip link set br3-router-trunk up
sudo ip link set br1-br3-trunk up
sudo ip link set br2-br3-trunk up
sudo ip link set router-trunk up
sleep 1

echo "--- OVS show..."
ovs-vsctl show

echo "--- Set VLAN trunk port... VLAN 100 intentionally not included in trunk"
ovs-vsctl set port br1-trunk trunks=100,200
ovs-vsctl set port br2-trunk trunks=100,200
ovs-vsctl set port br1-br3-trunk trunks=100,200
ovs-vsctl set port br2-br3-trunk trunks=100,200
ovs-vsctl set port br3-router-trunk trunks=100,200

echo "Enable routing ..."
ip netns exec router ip addr add 192.168.100.1/24 dev router-trunk
ip netns exec router ip addr add 192.168.200.1/24 dev router-trunk
sudo ip netns exec router sysctl -w net.ipv4.ip_forward=1

echo "--- Show OVS..."
ovs-vsctl show

echo "--- Add gateways to namespaces..."
ip netns exec yellow1 ip route add default via 192.168.100.1
ip netns exec green1 ip route add default via 192.168.200.1
ip netns exec yellow2 ip route add default via 192.168.100.1
ip netns exec green2 ip route add default via 192.168.200.1

echo "--- Show OVS..."
ovs-vsctl show
