from dronekit import connect, VehicleMode, LocationGlobalRelative, APIException
import time
import socket
#import exeptions
import math
import argparse

def arm_and_takeoff(altitude, vehicle):
	while vehicle.is_armable != True:
		print("Waiting for vehicle to become armable")
		time.sleep(1)
	print("Vehicle is now armable")

	vehicle.mode = VehicleMode("GUIDED")

	while vehicle.mode != 'GUIDED':
		print("Waiting for drone to enter GUIDED flight mode")
		time.sleep(1)
	print("Vehicle now in GUIDED Mode. habe fun !")

	vehicle.armed = True

	while vehicle.armed==False:
		print("Waiting for vehicle to become armed")
		time.sleep(1)
	print("look out! Virtual props are spinning!!")
	vehicle.simple_takeoff(altitude)

	while True:
		print("Current Altitude: %d" % vehicle.location.global_relative_frame.alt)
		if vehicle.location.global_relative_frame.alt >= .95*altitude:
			break
		time.sleep(1)

	print("Target altitude reached!!")

def get_distance_meters(target, current):
	dLat = target.lat - current.lat
	dLon = target.lon - current.lon

	return math.sqrt((dLon*dLon) + (dLat*dLat))*1.113195e5

def goto(target, vehicle):
	dis = get_distance_meters(target, vehicle.location.global_relative_frame)
	vehicle.simple_goto(target)

	while vehicle.mode.name == "GUIDED":
		currentdis = get_distance_meters(target, vehicle.location.global_relative_frame)
		if currentdis < dis * .01:
			print("Reached target waypoint")
			time.sleep(2)
			break
		time.sleep(1)
	return None


#####################main##########


