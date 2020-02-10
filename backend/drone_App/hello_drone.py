
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative, Command, LocationGlobal, APIException
from pymavlink import mavutil
import socket
import math

def connectMyCopter():
	import dronekit_sitl
	sitl = dronekit_sitl.start_default()
	connection_string = sitl.connection_string()
	vehicle = connect(connection_string, wait_ready=True)
	vehicle.wait_ready(True, raise_exception=False)

	return vehicle

def arm_and_takeoff(altitude):
	while not vehicle.is_armable:
		print ("Waiting for vehicle to initialise...")
		time.sleep(1)
	print ("Arming motors")
	vehicle.mode = VehicleMode("GUIDED")
	vehicle.armed = True
	while not vehicle.armed:
		print (" Waiting for arming ...")
		time.sleep(1)

	print("Taking off!")
	vehicle.simple_takeoff(altitude)
	while True:
		print (" Altitude: ", vehicle.location.global_relative_frame.alt)
		#Break and return from function just below target altitude.
		if vehicle.location.global_relative_frame.alt>=altitude*0.95:
			print ("Reached target altitude")
			break
		time.sleep(1)

def changeMode(vehicle, mode):
	while vehicle.mode != VehicleMode(mode):
		vehicle.mode = VehicleMode(mode)
		time.sleep(0.5)
	return True

#vehicle = connectMyCopter()
#print ("Get some vehicle attribute values:")
#print (" GPS: %s" % vehicle.gps_0)
#print (" Battery: %s" % vehicle.battery)
#print (" Last Heartbeat: %s" % vehicle.last_heartbeat)
#print (" Is Armable?: %s" % vehicle.is_armable)
#print (" System status: %s" % vehicle.system_status.state)
#print (" Mode: %s" % vehicle.mode.name)

#arm_and_takeoff(2)

#time.sleep(10)
#print("LAND mode")
#changeMode(vehicle,"LAND")
#print("Finish")
