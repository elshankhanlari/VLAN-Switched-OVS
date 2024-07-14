#!/bin/bash

echo "---Deleteing ovs bridges..."
ovs-vsctl del-br br1
ovs-vsctl del-br br2
ovs-vsctl del-br br3
sleep1

echo "---Setting up environment..."
ip route flush table main
systemctl restart networking
systemctl restart openvswitch-switch
sleep1

echo "---echo Verify Clean Environment..."
ifconfig
ovs-vsctl show
ip addr show
