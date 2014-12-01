#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Project_code.py
#############################################################


import os
import glob
import time
from time import sleep
import RPi.GPIO as GPIO
import numpy
import gps
import labview_comm
import temperature_data


###########################################################
#Global Variables

Temperature_Status = 0 #Sets the status of temperature as low for default
Motion_Status = 0 #Sets the status of motion as low for default

	
##########################################################
#Defines the function of GPS
def check_gps():
	#listen on port 2947 (gpsd) of localhost
	session = gps.gps("localhost","2947")
	session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
	for i in range(5):
		try:
			report = session.next()
			#wait for a 'TPV' report and display the current time
			#To see all report data, uncomment the line below
			#print report
			if report['class']=='TPV':
				if hasattr(report,'time'):
					gps_time = report.time
			if report['class']=='TPV':
				if hasattr(report,'lon'):
					gps_longitude = report.lon 
			if report['class']=='TPV':
				if hasattr(report,'lat'): 
					gps_latitude = report.lat
		except KeyError:
			pass
		except KeyboardInterrupt:
			quit()
		except StopIteration:
			session=None
			print "GPSD has terminated"
	gps_complete = " Date and Time in UTC: " + str(gps_time) + " Longitude: " + str(gps_longitude) + " Latitude: " + str(gps_latitude)
	return gps_complete

##########################################################
	
#Defines the function of ir sensor
def ir_sensor_callback():
		
		print "baby detected"
		
        #case 1 low
		if Temperature_Status == 0:
			print "No Danger, Temperature Below 72 Degrees"
			      

        #case 2 mid
		if Temperature_Status == 1:
			print "Possible Danger, Temperature in Between 88 and 100 Degrees"
			

        #case 3 high
		if Temperature_Status == 2:
			print "Emergency!!! Occupant in Danger"
			execute_safety()
		
#######################################################################################
                
def check_temp_state():
		danger_zone = 100 #declaring 88 degrees as the start of the danger zone
		low_danger = 72	 #declaring 72 degress as the start of the safe zone
		print "Retrieving Average Temperature"
		temp_avg = temperature_data.get_temperature() 
		global Temperature_Status
        #case 1 low
		if temp_avg <= low_danger: 							#check if temperature is in the low zone
			print "low temperature @ " + str(temp_avg)      #print temperature 
			temperature_data.send_temp(temp_avg)			#send temperature to LabView
			Temperature_Status = 0							#sets global variable for temperature status 
        #case 2 mid
		if temp_avg > low_danger and temp_avg < danger_zone: #check if temperature is in the middle zone
			print "middle zone temperature @" + str(temp_avg)#print temperature
			temperature_data.send_temp(temp_avg) 			 #send temperature to LabView
			Temperature_Status = 1						     #sets global variable for temperature status
        #case 3 high
		if temp_avg >= danger_zone:							 #check if temperature is in the high zone
			print "emergency temperature @ " + str(temp_avg) #print temperature
			temperature_data.send_temp(temp_avg)			 #send temperature to LabView DAQ
			Temperature_Status = 2						     #sets global variable for temperature status
			
##########################################################################
		
def execute_safety():
		
	GPIO.output(24,True) #TURN ON ALARM
	GPIO.output(9,True) #LOWER THE WINDOW
	time.sleep(4)		 #Amount of time window motor will operate
	GPIO.output(9,False)#TURN OFF MOTOR
	gps_location = check_gps()
	print gps_location
	labview_comm.labview(gps_location)#establish client-server communication with LabView
	print "GPS SENT"
	while(GPIO.input(23) == False):#CHECK IF DOOR IS CLOSED
		sleep(0.1)
	deactivate_safety()
		
			
		
#################################################################

def deactivate_safety():
	GPIO.output(24,False) #TURN OFF ALARM
	Temperature_Status = 0 #Reset Temperature Status
		
#################################################################

def GPIO_INIT():
	
	GPIO.setwarnings(False)	#tells raspberry pi to ignore GPIO alarms
	
	GPIO.setmode(GPIO.BCM)	#tell the GPIO module that we want to use the chip's pin numbering scheme

	GPIO.setup(4,GPIO.IN) 	#temperature sensor
	GPIO.setup(17,GPIO.OUT) #BIT7
	GPIO.setup(27,GPIO.OUT) #BIT6
	GPIO.setup(22,GPIO.OUT) #BIT5
	GPIO.setup(5,GPIO.OUT)  #BIT4
	GPIO.setup(6,GPIO.OUT)  #BIT3
	GPIO.setup(13,GPIO.OUT) #BIT2
	GPIO.setup(26,GPIO.OUT) #BIT1
	GPIO.setup(16,GPIO.OUT) #BIT0
	GPIO.setup(14,GPIO.IN)	#IR SENSOR
	GPIO.setup(9,GPIO.OUT)	#WINDOW MOTOR DOWN
	GPIO.setup(23,GPIO.IN)	#DOOR SWITCH
	GPIO.setup(24,GPIO.OUT)	#ALARM
	GPIO.output(24, False)	#ALARM INITAL SETUP
	GPIO.output(9,False) 	#WINDOW MOTOR INITAL SETUP

#################################################################
	
def main():
	
	GPIO_INIT()	#Sets up the GPIO Pins
	
	print "system on"
	
	try:
		while True:
			if (GPIO.input(23)==False): #WHILE the door is closed the progran will check the temperature
				if GPIO.input(14):
					print "ir sensor tripped"
					check_temp_state()
					ir_sensor_callback()
					sleep(1)
				else:
					print "sensor not tripped"
				   #function call to check temperature
					sleep(3)
			else:
				print "door open"
				sleep(10)
	except KeyboardInterrupt:
			print ""
			print "Goodbye, have a nice day"

	finally:
		GPIO.cleanup()

######################################################################

if __name__=="__main__":
    main()

#######################################################################
