#!/bin/bash

echo "---Deleteing ovs bridges..."
ovs-vsctl del-br br1
ovs-vsctl del-br br2
ovs-vsctl del-br br3

echo "---Setting up environment..."
ip route flush table main
systemctl restart networking
systemctl restart openvswitch-switch
sleep 1

echo "---echo Verify Clean Environment..."
ifconfig
ovs-vsctl show
route -n
ip addr show
