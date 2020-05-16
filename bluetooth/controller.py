#  LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1.2.0 python3 controls.py

import RPi.GPIO as GPIO
import time
import prefs
import os
import errno
#import cv2 as cv2
import shutil
#import picamera

#camera = picamera.PiCamera()
#camera.capture('example.jpg')

# TODO Seperate the recorder code from this mess
# time.sleep(10) # Wait 10 seconds for server to start up
# cap = cv2.VideoCapture('http://localhost:8080/stream.mjpg')

# Forawrd / Backward Pins
in1 = 27
in2 = 17
en = 22

temp1=1

# Left / Right Pins
tin1 = 23
tin2 = 24
ten = 25

steering_angle = 75

GPIO.setmode(GPIO.BCM)
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en,GPIO.OUT)
GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)
p=GPIO.PWM(en,1000)
p.start(25)

GPIO.setup(tin1,GPIO.OUT)
GPIO.setup(tin2,GPIO.OUT)
GPIO.setup(ten,GPIO.OUT)
GPIO.output(tin1,GPIO.LOW)
GPIO.output(tin2,GPIO.LOW)
tp=GPIO.PWM(ten,1000)
tp.start(25)

global tank_controls
tank_controls = False;

def set_accel(accel_val):
    if accel_val>0:
        # Forward
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
    else:
        # Backwards
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.HIGH)
    p.ChangeDutyCycle(abs(accel_val))

global last_out
last_out = ""
def tank_mover(steering_angle, accel_val):
    global last_out
    out = "[TANK] "
    if accel_val>0:
        # Forward
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.HIGH)

        GPIO.output(tin1,GPIO.HIGH)
        GPIO.output(tin2,GPIO.LOW)
        
    elif accel_val<0:
        # Backwards
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)

        GPIO.output(tin1,GPIO.LOW)
        GPIO.output(tin2,GPIO.HIGH)
    else:
        if steering_angle>0:
            # Pure Left
            GPIO.output(in1,GPIO.LOW)
            GPIO.output(in2,GPIO.HIGH)
            GPIO.output(tin1,GPIO.LOW)
            GPIO.output(tin2,GPIO.HIGH)
        else:
            # Pure Right
            GPIO.output(in1,GPIO.HIGH)
            GPIO.output(in2,GPIO.LOW)
            GPIO.output(tin1,GPIO.HIGH)
            GPIO.output(tin2,GPIO.LOW)
        p.ChangeDutyCycle(abs(steering_angle * 100))
        tp.ChangeDutyCycle(abs(steering_angle * 100))

        out = "p" + str(abs(steering_angle)) + "; tp" + str(abs(steering_angle))
        if out!=last_out:
            print(out)
            last_out = out
        return

    tf = (steering_angle + 1)
    p.ChangeDutyCycle(abs(accel_val * tf/2.0))
    tp.ChangeDutyCycle(abs(accel_val * (1 - abs(tf)/2.0) * 2))
    
    out = "p" + str(abs(accel_val * tf)) + "; tp" + str(abs(accel_val * (1 - abs(tf))))
    if out!=last_out:
        print(out)
        last_out = out



def set_steering(steering_angle, accel_val=0):
    if steering_angle>0:
        # Left
        GPIO.output(tin1,GPIO.HIGH)
        GPIO.output(tin2,GPIO.LOW)
    else:
        # Right
        GPIO.output(tin1,GPIO.LOW)
        GPIO.output(tin2,GPIO.HIGH)
    tp.ChangeDutyCycle(abs(steering_angle)*100)


# PICS steering_angle speed throttle brakes
def loop(accel_val, steering_angle):
    global tank_controls

    rec = prefs.get_pref("rec")
    #accel_val = int(prefs.get_pref("accel_val"))
    #steering_angle = float(prefs.get_pref("steering_angle"))
    #accel_val = 40
    #steering_angle = 0.4
    #print(accel_val, steering_angle, sep=" -- ")
    #set_accel(accel_val)
    if tank_controls:
        tank_mover(steering_angle, accel_val)
    else:
        set_accel(accel_val)
        set_steering(steering_angle)


def corrected_reading(val):
    res = -1*(val-32767)/32767
    if res < -1:
        res = -1
    if res > 1:
        res = 1
    res = round(res, 4)
    return res

from evdev import InputDevice, categorize, ecodes

#creates object 'gamepad' to store the data
#you can call it whatever you like
gamepad = InputDevice('/dev/input/event0')

#prints out device info at start
print(gamepad)

while True:
    try:
        for event in gamepad.read_loop():
            accel_val = 0
            steering_angle = 0

            if event.type!=0:
                #filters by event type
                print(type(event.code), event.code)
                if event.code == 1:
                    accel_val = corrected_reading(event.value) * 100
                elif event.code == 2:
                    steering_angle = corrected_reading(event.value)

            loop(accel_val, steering_angle)
    except Exception as e:
        print(e)
