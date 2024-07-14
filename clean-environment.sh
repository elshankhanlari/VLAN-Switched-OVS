#!/bin/bash

echo "---Setting up environment..."
iptables -F
iptables -t nat -F
iptables -X
ip route flush table main
systemctl restart networking
systemctl restart openvswitch-switch
