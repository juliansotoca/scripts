#!/usr/bin/env python
import paramiko
import unicodedata
import string
import os
import commands
import sys
import socket
import subprocess

class Zona:
	def __init__(self, nombre):
		#print "Inicializada la zona", nombre
		self.nombre = nombre
	
	def ssh(self, comando):
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(self.nombre, username='root')
		stdin, stdout, stderr = ssh.exec_command(comando)
		return stdout.read()
			
	
	def hostname(self):
		nombre=self.ssh('hostname').splitlines()
		if isinstance(nombre[0],str):
			print nombre[0]
		else:
			print "No se puede establecer la conexion"
		
		
	def lista(self):
		comando='zoneadm list | grep -v global'
		zonas = self.ssh(comando).splitlines()
		if not isinstance(zonas, int):
			listado = ''
			for zona in zonas:
				if len(listado)>0:
					listado = listado +'; '+zona
				else:
					listado = listado + zona
			#print listado
			return zonas

	def memoria(self, zona):
		comando="rcapstat -z 1 1 |grep "+zona+" | awk '{print $6}'"
		memoria = self.ssh(comando).splitlines()
		if not isinstance(memoria, int):
			memoria = str(memoria[0])
	#		print zona+"--> Memoria: "+memoria
			return memoria
	def swap(self, zona):
		comando="prctl -n zone.max-swap -i zone "+zona+"$i | grep privileged | awk '{print $2}'"
		swap = self.ssh(comando).splitlines()
		if not isinstance(swap, int):
			swap = str(swap[0])
	#		print zona+"--> Swap: "+swap
			return swap
		
	def cpu(self, zona):
		comando="prctl -n zone.cpu-shares -i zone "+zona+"$i | grep privileged | awk '{print $2}'"
		cpu = self.ssh(comando).splitlines()
		if not isinstance(cpu, int):
			cpu = str(cpu[0])
	#		print zona+"--> CPU: "+cpu
			return cpu
	def gMemory(self):
		comando="prtconf |grep Memory"
		memoria = self.ssh(comando).splitlines()
		if not isinstance(memoria, int):
			#print memoria
			return memoria[0].split(' ')[2]
	def red(self):
		IP=socket.gethostbyname(self.nombre)
		if '10.150' in IP:
			segmento='DMZ-2'
		elif '192.168.150' in IP:
			segmento='DMZ'
		elif '192.168.156' in IP:
			segmento='BACKEND'
		else:
			segmento='OTRAS'
		return segmento
	def release(self):
		comando="uname -v"
		version=self.ssh(comando).splitlines()
		if not isinstance(version, int):
			return version[0].replace('Generic_','')
		

def parametros(zglobal,output):
	servidor = Zona(zglobal)
	try:
	#	print "Zona global: "+servidor.nombre+" Memoria: "+servidor.gMemory()+" MB"
		zonas=servidor.lista()
		#print zonas
		#servidor.hostname()
		if output == "csv":
			#print servidor.nombre+";"+servidor.gMemory()
			output=servidor.nombre+";"+servidor.gMemory()+";"+servidor.red()+";"+servidor.release()+";"
			#print "zona;CPU(%);Memoria;Swap;"
			for zona in zonas:
				output=output+zona +";"+servidor.cpu(zona)+";"+servidor.memoria(zona)+";"+servidor.swap(zona)+";"
				#print zona +";"+servidor.cpu(zona)+";"+servidor.memoria(zona)+";"+servidor.swap(zona)+";"
			print output
		elif output == "default":
			print "Zona global: "+servidor.nombre+" Memoria: "+servidor.gMemory()+" MB"
			print "Zona \t\tCPU (%) \tMemoria \tSwap"
			for zona in zonas:
				print zona +"\t"+servidor.cpu(zona)+"\t\t"+servidor.memoria(zona)+"\t\t"+servidor.swap(zona)
	except Exception, e:
		if str(e).find("Name or service not known")>=1:
			print "No se ha podido establecer la conexion con el servidor: "+servidor.nombre
		else:
			print "Error desconocido"
			print e
		

def listado_completo(servidores,output):
	for zglobal in servidores:
		parametros(zglobal,output)
		
def borraParametro(argumentos, parametro):
	for i in range(0,len(argumentos)):
			if (argumentos[i] == parametro):
				pos=i
	del argumentos[pos]
	


servidores = ['globalzone1', 'globalzone2', 'globalzone3']


if "--csv" in sys.argv:
	print "generando csv"
	print "zonaglobal;Memoria(MB);Red;Release;zona1;CPU;memoria;swap;zona2;CPU;memoria;swap;zona3;CPU;memoria;swap;zona4;CPU;memoria;swap;zona5;CPU;memoria;swap;"
	output="csv"
	while "--csv" in sys.argv:
		borraParametro(sys.argv, "--csv")
else:
	output="default"

if len(sys.argv) >=2:
	#servidores = sys.argv
	#del servidores[0]
	#for zglobal in servidores:
	for zglobal in sys.argv[1:len(sys.argv)]:
		parametros(zglobal,output)
		
else:
	listado_completo(servidores,output)
