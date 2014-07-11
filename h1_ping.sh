#!/bin/bash
rtt=1
PingCount=5
IP1=30.0.1.2

fping -e -q  $IP1 -c $PingCount 2> out.txt
cat out.txt | awk '{print $1" "$5" "$8}' | sed 's/\// /g' | sed 's/\%,/ /g' > host1.txt