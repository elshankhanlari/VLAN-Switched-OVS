#!/bin/bash

echo "Ping hosts on same VLAN=100...yellow1 to yellow2"
ip netns exec yellow1 ping -c 4 192.168.100.3

echo "Ping hosts on same VLAN=100...green2 to green1"
ip netns exec green2 ping -c 4 192.168.200.2

echo "Ping hosts on different VLANs...yellow1 to green2"
ip netns exec yellow1 ping -c 4 192.168.200.3

echo "Ping hosts on different VLANs...yellow2 to green1"
ip netns exec yellow2 ping -c 4 192.168.200.2
