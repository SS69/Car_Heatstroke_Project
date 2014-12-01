#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Client Program
import socket
import threading
import os
import sys
import select
from time import sleep

def labview(gps_location):
	class Transmit(threading.Thread):
		def run(self):
			# Sending data to the server
			#print('Transmit started')
			global s # connection
			global threadRunning

			#string = "car location: longitude = 69.9, latitude = 69.9"	
			string = gps_location
			byteArray = bytearray(string, "utf-8") # Convert string into a b$
			s.sendall(byteArray)
			#print('Transmit stopped - threadRunning')
			return

	# Running main program
	HOST = '192.168.0.113' # The remote host - windows machine running the LabVIEW Server
	PORT = 2055 # The same port as used by the server - defined in LabVIEW
	global threadRunning # Used to stop threads
	threadRunning = False
	global s
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))

	#os.system('clear')
	print('Connection with server established')
	transmit = Transmit()
	transmit.start()
	sleep(2)
	s.close()
