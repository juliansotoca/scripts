#!/usr/bin/env python
import paramiko
import unicodedata
import string
import os
import commands
import sys
import socket
import subprocess

class Server:
	
	def __init__(self, nombre):
		print "Inicializado el servidor %s" % nombre
		self.nombre = nombre
		self.updateList=[]
		self.toUpdate=[]
		
	def ssh(self, comando):
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(self.nombre, username='root')
		stdin, stdout, stderr = ssh.exec_command(comando)
		return stdout.read()
		
	def checkConectivity(self):
		try:
			self.ssh('hostname')
			#print "Succesfully connected to the server %s" % self.nombre
			return True
		except:
			print "Cannot connect to the server %s" % self.nombre
			return False
			
	def checkUpdates(self):
		updates=self.ssh('repoquery -a --pkgnarrow=updates --qf="%{name} %{arch} %{ver}-%{rel}"')
		
		i=1
		#print repr(updates)
		print "ID\t%s\t\t%s\t\t%s" % ( 'Package', 'Arch', 'Version')
		for line in updates.split('\n'):
			if line:
				try:
					pkg,arch,version=line.split()
					#pkg = line.split('-')[0].split('.')[0]
					#arch = line.split()[0].split('.')[1]
					#version = line.split()[1]
					print "%d\t%s\t\t%s\t\t%s" % (i, pkg, arch, version)
					i=i+1
					self.updateList.append([pkg, arch, version])
				except:
					print "Problems parsing %s" % line
	def installUpdates(self):
		packages = ''
		for p in self.toUpdate:
			packages = packages +' '+p[0]
		print 'yum -q -y update %s' % packages
		output = self.ssh('yum -q -y update %s' % packages)

def listUpdates(s):
	os.system('clear')
	print "Updates"
	s.checkUpdates()
	print "-"*40
	print "1. Select packages to update"
	print "2. Exit"
	print "-"*40
	x = raw_input("Select an option: ")
	if ( x == '1' ):
		s.toUpdate=[]
		a = raw_input("Update ALL packages (Y/n) ")
		if ( a.lower() == 'y' ) :
			s.toUpdate=s.updateList
		else:
			for p in s.updateList:
				r = raw_input("Update %s to version %s (Y/n) " % (p[0], p[2]))
				if (r.lower()=='y'):
					s.toUpdate.append(p)
		if len(s.toUpdate)>0:
			os.system('clear')
			print "Selected packages to update: "
			print "Package\t\tArch.\t\tVersion"
			for p in s.toUpdate:
				print "%s\t\t%s\t\t%s" % (p[0],p[1], p[2])
		return
	elif ( x == '2'):
		return
	else:
		os.system('clear')
		print "Bad option"
		raw_input('Pres ENTER to continue.')
	
def installUpdates(s):
	os.system('clear')
	print "Install Updates"
	print "You are going to update those packages:"
	for p in s.toUpdate:
		print "%s" % p[0]
	c = raw_input('Continue? (Y/n)')
	if (c.lower()=='y'):
		s.installUpdates()

def mainMenu(s):
	#os.system('clear')
	print "1. List updates"
	print "2. Install updates"
	print "3. Exit"
	x = raw_input("Select an option: ")
	if ( x == '1' ):
		listUpdates(s)
	elif ( x == '2' ):
		installUpdates(s)
	elif ( x == '3'):
		exit()
	else:
		os.system('clear')
		print "Bad option"
		raw_input('Pres ENTER to continue.')

def main():
	if len(sys.argv) >=2:
		server = sys.argv[1]
	else:
		server = raw_input("Enter the IP address or the name server you want to manage: ")
	s = Server(server)	
	
	while True:
		if s.checkConectivity():
			print "Selected server: %s" % s.nombre
			mainMenu(s)
		else:
			server = raw_input("Enter the IP address or the name server you want to manage or X to exit: ")
			if ( server.lower() == 'x' ):
				exit()
			else:
				s = Server(server)
				

if __name__ == "__main__":
	main()
