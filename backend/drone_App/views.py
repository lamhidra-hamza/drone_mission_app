from django.shortcuts import render
from .hello_drone import connectMyCopter ,changeMode
from threading import Thread
from drone_App import models
import time
from .gotowaypoint import arm_and_takeoff, goto
from django.core import serializers
from pymercure.publisher.sync import SyncPublisher
from pymercure.message import Message
from .serializers import vehicleSerializer
from rest_framework import status, generics
from rest_framework.response import Response
from dronekit import connect, VehicleMode, LocationGlobalRelative, Command, LocationGlobal, APIException
from pymavlink import mavutil
import json
import math

# Create your views here.

sa = 0

def Drone():
    global sa

    while (1):
        #print("Hello")
        if (sa == 0):
            sa = connectMyCopter()
        models.Vehicle.objects.all().update(lat=sa.location.global_relative_frame.lat)
        models.Vehicle.objects.all().update(longt=sa.location.global_relative_frame.lon)
        models.Vehicle.objects.all().update(alt=sa.location.global_relative_frame.alt)
        models.Vehicle.objects.all().update(battery=sa.battery)
        models.Vehicle.objects.all().update(mode=sa.mode.name)
        models.Vehicle.objects.all().update(arm=sa.is_armable)
        vehi = models.Vehicle.objects.all()
        serialized_obj = serializers.serialize('json',vehi)
        msg = Message(['drone'], serialized_obj)
        publisher = SyncPublisher(
            'http://10.1.34.172:3000/.well-known/mercure',
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtZXJjdXJlIjp7InB1Ymxpc2giOlsiKiJdfX0.obDjwCgqtPuIvwBlTxUEmibbBf0zypKCNzNKP7Op2UM'
        )
        publisher.publish(msg)
        time.sleep(0.1)

def goto_this():
    global sa

    wp1 = LocationGlobalRelative(44.50202, -88.060316, 10)
    arm_and_takeoff(10, sa)
    goto(wp1,sa)

class Vehicle_info(generics.ListAPIView):
    queryset = models.Vehicle.objects.all()
    serializer_class = vehicleSerializer

class Start(generics.RetrieveUpdateDestroyAPIView):
    global sa

    if (sa == 0):
        sa = connectMyCopter()
        thread = Thread(target=Drone)
        thread.start()


######### all function bellow are for doing missions ######

def arm_and_takeoff(altitude, vehicle):
	while not vehicle.is_armable:
		print ("Waiting for vehicle to initialise...")
		time.sleep(1)
	print ("Arming motors")
	vehicle.mode = VehicleMode("GUIDED")
	vehicle.armed = True
	while not vehicle.armed:
		print (" Waiting for arming ...")
		time.sleep(1) 

	print( "Taking off!")
	vehicle.simple_takeoff(altitude)
	while True:
		print (" Altitude: ", vehicle.location.global_relative_frame.alt)
		#Break and return from function just below target altitude.
		if vehicle.location.global_relative_frame.alt>=altitude*0.95:
			print ("Reached target altitude")
			break
		time.sleep(1)

def download_mission(vehicle):

	cmds = vehicle.commands
	cmds.download()
	cmds.wait_ready()

def get_target(target):
	lat = target.x
	lon = target.y
	alt = target.z
	ret = LocationGlobalRelative(lat, lon, alt)
	return ret

def changeMode(vehicle, mode):
	while vehicle.mode != VehicleMode(mode):
		vehicle.mode = VehicleMode(mode)
		time.sleep(0.5)
	return True

def get_distance_metres(aLocation1, aLocation2):
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

def add_full_mission(missionlst, vehicle):
	dis1 = get_distance_metres(get_target(missionlst[0]), get_target(missionlst[1]))
	dis2 = get_distance_metres(get_target(missionlst[1]), get_target(missionlst[2]))
	num = dis2 / 3
	i = 0
	n = 2
	n1 , n2 = 1, 1
	xA = missionlst[0].x
	yA = missionlst[0].y
	xB = missionlst[1].x
	yB = missionlst[1].y
	xC = missionlst[2].x
	yC = missionlst[2].y
	xD = missionlst[3].x
	yD = missionlst[3].y
	disBC = math.sqrt((xC - xB)*(xC - xB) + (yC - yB)*(yC - yB))
	disAD = math.sqrt((xD - xA)*(xD - xA) + (yD - yA)*(yD - yA))
	l1 = 1
	l2 = 0
	while (i / 2 < num - 1):
		if (l1 != 0):
			x = xB - ((n1 * (disBC/num)) * (xB - xC)) / disBC
			y = yB - ((n1 * (disBC/num)) * (yB - yC)) / disBC
			l1 -= 1
			if l1 == 0:
				l2 = 2
			n1 += 1
		elif l2 != 0:
			x = xA - ((n2 * (disAD/num)) * (xA - xD)) / disAD
			y = yA - ((n2 * (disAD/num)) * (yA - yD)) / disAD
			l2 -= 1
			if l2 == 0:
				l1 = 2
			n2 += 1
		wp1 = Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
					0, 0, 0, 0, 0, 0,
					x, y, 10)
		missionlst.insert(n, wp1)
		n += 1
		i += 1
	download_mission(vehicle)
	cmds = vehicle.commands
	cmds.clear()
	for wp in missionlst:
		cmds.add(wp)
	cmds.upload()
	time.sleep(5)

def clear_mission(vehicle):
	cmds = vehicle.commands
	cmds.clear()
	cmds.upload()
	download_mission(vehicle)

class Vehicle_p(generics.CreateAPIView):
    def post(self, request):
        global sa
        mission_data = request.data
        missionlst = []
        i = 0
        for l in mission_data:
            if i == 5:
                return Response("Error")
            wp = Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
					0, 0, 0, 0, 0, 0,
					l['latitude'], l['longitude'], 0)
            print(wp)
            missionlst.append(wp)
            i += 1

        if i != 4:
            return Response("Error")
        speed = 5
        mode = 'ground'
        while True:
            if mode == 'ground':
                add_full_mission(missionlst, sa)
                time.sleep(2)
                print("there is a mission, lets taking off")
                mode = 'takeoff'
            
            elif mode == 'takeoff':
                arm_and_takeoff(10, sa)
                changeMode(sa,"AUTO")
                sa.groundspeed = speed
                mode = 'mission'
                print("switch to mission mode")
            elif mode == 'mission':
                print("current wp: %d of %d " % (sa.commands.next, sa.commands.count))
                if (sa.commands.next == sa.commands.count):
                    print ("final wp reached: go back home")
                    clear_mission(sa)
                    changeMode(sa, "RTL")
                    mode = "back"
            elif mode == 'back':
                if (sa.location.global_relative_frame.alt < 1.0):
                    print ("ground vehicle")
                    break
            time.sleep(0.5)
        return Response("ok")
