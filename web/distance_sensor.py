###
# Plotter Code
###
#
import numpy as np
import sys
import prefs

# Serial Comms
import random

import time
import serial
from math import sin, cos, pi, atan

def start_scan():
    #input("Enter to start")
    print("Connecting to serial")
    s = False
    for i in range(4):
        COM_PORT = "/dev/ttyUSB" + str(i)
        print("Trying to connect to", COM_PORT)
        try:
            s = serial.Serial(COM_PORT, 115200)
            break
        except:
            print("FAILED", COM_PORT)
            time.sleep(1)

    if s==False:
        print("No COM PORTS found")
        return

    POINTS = []
    while True:
        try:
            time.sleep(0.2)
            s.write(1)
            r, theta, phi = list(map(int, s.readline().split()))
            #r, phi, theta = list(map(int, s.readline().split()))
            #print("Analysing", [r, theta, phi])

            if r==0:
                raise Exception("r == 0")
            # r = r + (random.uniform(-0.3, 0.3))
            phi = phi - 100
            theta = theta + 90

            theta = theta * pi/180
            phi = phi * pi/180

            #r = r/3.125 # Scaling 
            #r = r*0.8 # Scaling 

            sf = 1
            d = 2.7 * sf
            R = 1.2 * sf

            phi_d = atan( ( (r+R)*sin(phi) + d*cos(phi) ) / ( (r+R)*cos(phi) - d*sin(phi) ) )
            r_d = ( (r+R)*cos(phi) - d*sin(phi) )/cos(phi)

            #r = r_d
            #phi = phi_d

            dist = r*cos(phi)
            if dist < 15: # Distance in cm
                print("Too close ", {"r": r, "dist": dist})
            
            POINTS.append([r, theta, phi, dist])
            if len(POINTS) > 6:
                print("Saving to distance_sensor")
                prefs.set_pref("distance_sensor", str(POINTS))
                POINTS = []

        except Exception as e:
            print(e)


start_scan()