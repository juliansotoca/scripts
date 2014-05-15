#!/bin/bash
function static {
	hostname=`hostname`
	read -r -p "Hostname: [${hostname}] " hostname
	if [ -z "$hostname" ]; then hostname=`hostname`; fi
	read -r -p "IP address: " ip
	read -r -p "Netmask: " mask
	grep dhcp /etc/sysconfig/network-scripts/ifcfg-eth* 2>/dev/null >/dev/null
	if [ $? -eq 0 ] ; then
		echo "there is a network configured with dhcp which should configure your gateway"
	else
		read -r -p "Gateway: " gate
		if [ $? -eq 0 ] ; then
			sed -i -e 's#^\(GATEWAY=\).*$#\1'"${gate}"'#' /etc/sysconfig/network
		else
			echo "GATEWAY=\"${gate}\"" >>/etc/sysconfig/network
		fi
	fi
	#echo "HOSTNAME: ${hostname}\tIP: ${ip}\tNETMASK: ${mask}"
	mac=`ifconfig ${iface} | grep eth | awk '{ print $5}'`
	if [ -f /etc/sysconfig/network-scripts/ifcfg-${iface} ]; then
		rm -r /etc/sysconfig/network-scripts/ifcfg-${iface}
	fi
	echo "DEVICE=\"${iface}\"" >> /etc/sysconfig/network-scripts/ifcfg-${iface}
	echo "BOOTPROTO=\"static\"" >> /etc/sysconfig/network-scripts/ifcfg-${iface}
	echo "NM_CONTROLLED=\"yes\"" >> /etc/sysconfig/network-scripts/ifcfg-${iface}
	echo "ONBOOT=\"yes\"" >> /etc/sysconfig/network-scripts/ifcfg-${iface}
	echo "TYPE=\"Ethernet\"" >> /etc/sysconfig/network-scripts/ifcfg-${iface}
	echo "IPADDR=\"${ip}\"" >> /etc/sysconfig/network-scripts/ifcfg-${iface}
	echo "NETMASK=\"${mask}\"" >> /etc/sysconfig/network-scripts/ifcfg-${iface}
	echo "HWADDR=\"${mac}\"" >> /etc/sysconfig/network-scripts/ifcfg-${iface}
	echo "DNS1=\"10.82.150.113\"" >> /etc/sysconfig/network-scripts/ifcfg-${iface}
	echo "DNS2=\"192.168.150.113\"" >> /etc/sysconfig/network-scripts/ifcfg-${iface}
	echo "DOMAIN=\"globalia.com\"" >> /etc/sysconfig/network-scripts/ifcfg-${iface}
	sed -i -e 's#^\(HOSTNAME=\).*$#\1'"${hostname}"'#' /etc/sysconfig/network
	grep GATEWAY /etc/sysconfig/network 2>/dev/null >/dev/null
	
}

function dhcp {
	echo "Configuring DHCP for ${iface}"
	hostname=`hostname`
	read -r -p "Hostname: [${hostname}] " hostname
	if [ -z "$hostname" ]; then hostname=`hostname`; fi
	mac=`ifconfig ${iface} | grep eth | awk '{ print $5}'`
	if [ -f /etc/sysconfig/network-scripts/ifcfg-${iface} ]; then
		rm -r /etc/sysconfig/network-scripts/ifcfg-${iface}
	fi
	echo "DEVICE=\"${iface}\"" >> /etc/sysconfig/network-scripts/ifcfg-${iface}
	echo "BOOTPROTO=\"dhcp\"" >> /etc/sysconfig/network-scripts/ifcfg-${iface}
	echo "HWADDR=\"${mac}\"" >> /etc/sysconfig/network-scripts/ifcfg-${iface}
	echo "NM_CONTROLLED=\"yes\"" >> /etc/sysconfig/network-scripts/ifcfg-${iface}
	echo "ONBOOT=\"yes\"" >> /etc/sysconfig/network-scripts/ifcfg-${iface}
	echo "TYPE=\"Ethernet\"" >> /etc/sysconfig/network-scripts/ifcfg-${iface}
	sed -i -e 's#^\(HOSTNAME=\).*$#\1'"${hostname}"'#' /etc/sysconfig/network
}


ifconfig eth0 2>/dev/null >/dev/null
if [ $? -ne 0 ] ; then
	echo "eth0 not found. Interface configuration..."
	echo "Recreating interfaces"
	# Rename eth1 with eth0    
	echo "Stopping network"
	service network stop

#Clearing devices and renaming	
	echo "UDEV Config..."
	rm -f /etc/udev/rules.d/70-persistent-net.rules
	#ls -l  /etc/udev/rules.d/70-persistent-net.rules
	udevadm trigger
	sleep 2
	#ls -l  /etc/udev/rules.d/70-persistent-net.rules
	ifdevs=`udevadm info --export-db | grep "INTERFACE=eth" | cut -d "=" -f2`
	#echo "Interfaces ${ifdevs}"
	count=0
	for ifdev in ${ifdevs}; do
		sed -i -e "s/${ifdev}/eth${count}/g" /etc/udev/rules.d/70-persistent-net.rules
	#	echo "sed -i -e 's/${ifdev}/eth${count}/g' /etc/udev/rules.d/70-persistent-net.rules"
		count=$((count+1))
	#	echo "count: ${count}"
	done
	udevadm trigger --attr-match=subsystem=net
	
	#echo "udev Net rules"
	#grep eth /etc/udev/rules.d/70-persistent-net.rules
    echo "---------------------------------------------------"
    
#Clearing configuration    
	echo "Remove previous configuration"
	for cfgfile in `ls /etc/sysconfig/network-scripts/ifcfg-eth*`; do
		read -r -p "Remove previous configuration file ${cfgfile}? [y/N] " response
		case $response in
			[yY])
				rm -f ${cfgfile}
				;;
			*)
				echo "Not removing ${cfgfile}"
				;;
		esac
	done
    
#Setup ehternet devices
	sleep 2
	ifaces=`ifconfig -a | grep eth | awk '{ print $1}'`
	#echo ${ifaces}
	for iface in ${ifaces}; do
		read -r -p "Do you want to configure a static IP for ${iface}? [y/N] " response
		case $response in
			[yY])
				static
				;;
			*)
				read -r -p "Do you want to configure DHCP for ${iface}? [y/N] " respdhcp
				case $respdhcp in
					[yY])
						dhcp
						;;
					*)
						echo "Not configuring ${iface}."
						#rm -r /etc/sysconfig/network-scripts/ifcfg-${iface}
						;;
				esac
				;;
		esac
	done		
	
#Start networking
	
	echo "Starting networking"
	service network start
	
	
fi


