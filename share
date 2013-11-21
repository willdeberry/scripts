#!/bin/sh
# Share the VPN connection with other machines on the local net.
# The assumption here is the the VPN network is 10.0.0.0.
if [ `id -u` -ne 0 ] ; then
   echo "You are not root.  Rerunning with sudo..."
   sudo $0
else
   echo "1" > /proc/sys/net/ipv4/ip_forward
   iptables -A FORWARD -i wlan0 -d 10.0.0.0/8 -j ACCEPT
   iptables -t nat -A POSTROUTING -o tun0 -j MASQUERADE
   sysctl net.netfilter.nf_conntrack_acct=1
fi
