#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gps
import os
import glob
import time
import RPi.GPIO as GPIO
import numpy
import labview_comm
import temperature_data

from time import sleep
##############################################################
def get_temperature():
		os.system('modprobe w1-gpio')
		os.system('modprobe w1-therm')
		base_dir = '/sys/bus/w1/devices/'
		device_folder = glob.glob(base_dir + '28*')[0]
		device_file = device_folder + '/w1_slave'

		def read_temp_raw():
			f = open(device_file, 'r')
			lines = f.readlines()
			f.close()
			return lines

		def read_temp():
				lines = read_temp_raw()
				while lines[0].strip()[-3:] != 'YES':
						time.sleep(0.2)
						lines = read_temp_raw()
				equals_pos = lines[1].find('t=')
				if equals_pos != -1:
					temp_string = lines[1][equals_pos+2:]
					temp_c = float(temp_string) / 1000.0
					temp_f = temp_c * 9.0 / 5.0 + 32.0
					return temp_f
		temp_list=[]
		for x in range(10):
			temp_list.append(read_temp())

		temp_avg = round(numpy.mean(temp_list[0:9]),2)
		print "temperature= ",temp_avg

		return int(temp_avg)

###########################################################
def send_temp(Average_Temperature):
	#send temperature to lab view
	pin_array = [17,27,22,5,6,13,26,16]
	temp = Average_Temperature
	#temp = 99
	temp_binary = bin(temp)[2:].zfill(8)
	print "temperature in decimal = ", temp
	print "temperature in binary = ", temp_binary

	temp_array = [int(x) for x in str(temp_binary)]

	count = 0
	for n in temp_array:
		if n == 1:
			print "send 1 to DAQ pin ", pin_array[count]
			GPIO.output(pin_array[count],True)
		if n == 0:
			print "send 0 to DAQ pin ", pin_array[count]
			GPIO.output(pin_array[count],False)
		count += 1	
