#!/bin/sh

echo "Stop ONOS docker container"
sudo docker stop onos
sleep 2

echo "Remove ONOS docker container"
sudo docker rm onos
sleep 20

echo "Start ONOS docker container"
sudo docker run -t -d --name onos onosproject/onos
sleep 60

echo "Configure ONOS docker container"
./sdn-configure.sh
sleep 2
