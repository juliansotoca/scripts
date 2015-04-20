#!/usr/bin/python
#
# zoneadm list output
# zoneadm list -cv
#  ID NAME             STATUS     PATH                          BRAND    IP    
#   0 global           running    /                             native   shared
#   5 zone1		running    /zonas/zone1			native   shared
#   7 zone2		running    /zonas/zone2			native   shared
#   - zone3		installed  /zonas/zone3			native   shared
#
#
from subprocess import *

p = Popen(['hostname'], stdout=PIPE, stderr=PIPE)
hostname, err = p.communicate() 

p = Popen(['zoneadm', 'list', '-cv'], stdout=PIPE, stderr=PIPE)
zoneList, err = p.communicate()

for zone in zoneList.splitlines():
	name = zone.split()[1]
	if (name =='NAME') or (name == 'global'): continue
	cfgfile = "/zonas/%s/root/etc/GLOBALZONE" % name
	
	try:	
		f = open(cfgfile, "w")
		f.write(hostname)
		f.close()
	except:
		pass

	

