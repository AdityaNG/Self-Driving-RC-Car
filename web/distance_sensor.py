###
# Plotter Code
###
#
import numpy as np
import sys
import prefs

# Serial Comms
import random

import serial
from math import sin, cos, pi, atan

def start_scan():
    #input("Enter to start")
    print("Connecting to serial")
    s = serial.Serial("/dev/ttyUSB0", 115200)
    POINTS = []
    while True:
        try:
            s.write(1)
            r, theta, phi = list(map(int, s.readline().split()))
            #r, phi, theta = list(map(int, s.readline().split()))
            print("Analysing", [r, theta, phi])

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

            if len(POINTS)>25:
                prefs.set_pref("distance_sensor", str(POINTS))
                POINTS = []

            dist = r*cos(phi)
            if dist < 15: # Distance in cm
                print("Too close ", {"r": r, "dist": dist})
                
        except Exception as e:
            print(e)


start_scan()