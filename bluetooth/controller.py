#  LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1.2.0 python3 controls.py

import RPi.GPIO as GPIO
import time
import prefs
import os
import errno
import shutil
import threading
import sys

import cv2
import numpy as np

def log(*a):
    print("[CONT]", a)

#import sys
#sys.path.append("../self_drive")
#import drive
AUTOPILOT = False
sys.path.append("../self_drive")
import image_processing

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

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

ir_pin = 21
GPIO.setup(ir_pin,GPIO.IN)

wheel_speed_pow_pin = 26
GPIO.setup(wheel_speed_pow_pin,GPIO.OUT)
GPIO.output(wheel_speed_pow_pin,GPIO.HIGH)

wheel_speed_data_pin = 19
GPIO.setup(wheel_speed_data_pin,GPIO.IN)
#GPIO.output(wheel_speed_data_pin,GPIO.HIGH)


"""
# GPIO Pins don't provide enough current to drive Fan
FAN_PIN = 12
GPIO.setup(FAN_PIN,GPIO.OUT)
GPIO.output(FAN_PIN,GPIO.HIGH)
"""
BUZZER_PIN = 12
GPIO.setup(BUZZER_PIN,GPIO.OUT)
GPIO.output(BUZZER_PIN, GPIO.LOW)

def BACKGROUND_BUZZER_PATTERN(pattern_total, delay_time=0.5):
    for pattern in pattern_total:
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        if " " != str(pattern):
            GPIO.output(BUZZER_PIN, GPIO.HIGH)        
        time.sleep(delay_time)
    GPIO.output(BUZZER_PIN, GPIO.LOW)


# TODO : Play out complex LED patterns async
def BUZZER_PATTERN(pattern_total, delay_time=0.5):
    BUZZER_thread = threading.Thread(target=BACKGROUND_BUZZER_PATTERN, args=(pattern_total, delay_time))
    BUZZER_thread.start()

GPIO.output(BUZZER_PIN,GPIO.HIGH)

BUZZER_PATTERN("b", 0.1)

RED_PIN = 10
GREEN_PIN = 11
BLUE_PIN = 9

GPIO.setup(RED_PIN,GPIO.OUT)
GPIO.setup(GREEN_PIN,GPIO.OUT)
GPIO.setup(BLUE_PIN,GPIO.OUT)

def BACKGROUND_LED_PATTERN(pattern_total, delay_time=0.5):
    GPIO.output(RED_PIN,GPIO.HIGH)
    GPIO.output(GREEN_PIN,GPIO.HIGH)
    GPIO.output(BLUE_PIN,GPIO.HIGH)

    for pattern in pattern_total:
        GPIO.output(RED_PIN,GPIO.HIGH)
        GPIO.output(GREEN_PIN,GPIO.HIGH)
        GPIO.output(BLUE_PIN,GPIO.HIGH)
        if "R" == str(pattern):
            GPIO.output(RED_PIN,GPIO.LOW)
        elif "G" == str(pattern):
            GPIO.output(GREEN_PIN,GPIO.LOW)
        elif "B" == str(pattern):
            GPIO.output(BLUE_PIN,GPIO.LOW)
        elif " " == str(pattern):
            pass # All blank
        time.sleep(delay_time)
    
    GPIO.output(RED_PIN,GPIO.HIGH)
    GPIO.output(GREEN_PIN,GPIO.HIGH)
    GPIO.output(BLUE_PIN,GPIO.HIGH)
    if (str(pattern_total).endswith("_")):
        pattern = pattern_total[len(pattern_total)-2]
        if "R" == str(pattern):
            GPIO.output(RED_PIN,GPIO.LOW)
        elif "G" == str(pattern):
            GPIO.output(GREEN_PIN,GPIO.LOW)
        elif "B" == str(pattern):
            GPIO.output(BLUE_PIN,GPIO.LOW)
        elif " " == str(pattern):
            pass # All blank


# TODO : Play out complex LED patterns async
def LED_PATTERN(pattern_total, delay_time=0.5):
    LED_thread = threading.Thread(target=BACKGROUND_LED_PATTERN, args=(pattern_total, delay_time))
    LED_thread.start()


def connect_bluetooth_loop():
    BUZZER_PATTERN("b b", 0.1)
    # Bluetooth connect 
    while not bluetooth_connected():
        LED_PATTERN("B B B B B_", 0.25)
        os.system('./bluetooth_connect.sh')
        time.sleep(10) # Wait

    BUZZER_PATTERN("b b", 0.1)
    LED_PATTERN("B B G G G G G_", 0.25)


def bluetooth_connected():
    return "event0" in os.listdir("/dev/input/")


if not bluetooth_connected():
    connect_bluetooth_loop()


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
            #log(out)
            last_out = out
        return

    tf = (steering_angle + 1)
    p.ChangeDutyCycle(abs(accel_val * tf/2.0))
    tp.ChangeDutyCycle(abs(accel_val * (1 - abs(tf)/2.0) * 2))
    
    out = "p" + str(abs(accel_val * tf)) + "; tp" + str(abs(accel_val * (1 - abs(tf))))
    if out!=last_out:
        #log(out)
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


LAST_DATA = dict()

def autopilot_loop():
    global LAST_DATA
    while True:
        try:
            if AUTOPILOT:
                prefs.set_pref("AUTOPILOT", "1")
                now = time.time()
                accel_val = 0
                steering_angle = 0
                try:
                    accel_val = float(prefs.get_pref("accel_val_auto"))
                except:
                    log("accel_val_auto error")
                    pass
                try:
                    steering_angle = float(prefs.get_pref("steering_angle_auto"))
                except:
                    log("steering_angle_auto error")
                    pass
                    #accel_val, steering_angle = drive.telemetry(LAST_DATA, recorder.CURRENT_FRAME)

                if abs(prefs.get_pref_time("accel_val_auto") - now) <= 0.5 or abs(prefs.get_pref_time("steering_angle_auto") - now) <= 0.5:
                    loop(accel_val, steering_angle)
                    LAST_DATA["accel_val"] = accel_val
                    LAST_DATA["steering_angle"] = steering_angle
                    LAST_DATA["speed"] = prefs.get_pref("speed") #chase_value(accel_val, LAST_DATA["speed"], 0.25)
                    #prefs.set_pref("speed", LAST_DATA["speed"])
            else:
                prefs.set_pref("AUTOPILOT", "0")

            time.sleep(0.1)
        except Exception as e:
            log("AUTOPILOT - ", e)


AUTOPILOT_thread = threading.Thread(target=autopilot_loop)
AUTOPILOT_thread.start()

# PICS steering_angle speed throttle brakes
def loop(accel_val, steering_angle, rec_toggle=False):
    global tank_controls

    if rec_toggle:
        if prefs.get_pref("rec")=="0":
            BUZZER_PATTERN("b b b", 0.3)
            LED_PATTERN("R R_")
            log("Rec ON")
            prefs.set_pref("rec", str(time.time()))
        else:
            BUZZER_PATTERN("b", 1)
            LED_PATTERN("R R")
            log("Rec OFF")
            prefs.set_pref("rec", "0")

    speed = prefs.get_pref("speed")

    if AUTOPILOT:
        log("accel_val", round(accel_val, 3), "steering_angle", round(steering_angle, 3), "speed", speed, "[AUTOPilot]")
    else:
        log("accel_val", round(accel_val, 3), "steering_angle", round(steering_angle, 3), "speed", speed, "[MANUAL]")

    av = str(accel_val)
    prefs.set_pref("accel_val", av)
    
    sa = str(steering_angle)
    prefs.set_pref("steering_angle", sa)

    if tank_controls:
        tank_mover(steering_angle, accel_val)
    else:
        set_accel(accel_val)
        set_steering(steering_angle)

# Chase factor is a number less than 1. The larger it is, the more agressive is the chase
def chase_value(goal, chase, chase_factor=0.5):
    return chase + (goal-chase)*chase_factor

def corrected_reading(val):
    res = -1*(val-32767)/32767
    if res < -1:
        res = -1
    if res > 1:
        res = 1
    res = round(res, 4)
    return res


def decodeImage(image_bytes):
    return cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)


wheel_speed_counter = 0
wheel_speed_counter_last_set = time.time()
wheel_speed_delay = 1 # Calculate every 1 seconds
def speed_calculator():
    global wheel_speed_counter, wheel_speed_counter_last_set, wheel_speed_delay
    time.sleep(10) 
    while True:
        try:

            reading = GPIO.input(wheel_speed_data_pin)  
            if reading:
                wheel_speed_counter += 1
            
            now = time.time()
            if abs(now - wheel_speed_counter_last_set)>=wheel_speed_delay:
                log("speed_calculator - counts", wheel_speed_counter)
                wheel_speed_counter_last_set = now
                wheel_speed_counter = 0

            log("speed_calculator", reading)

            #speed = float(prefs.get_pref("speed"))
            #accel_val = float(prefs.get_pref("accel_val"))
            #speed = chase_value(accel_val, speed, 0.5)

            #global Camera
            #frame = decodeImage(Camera().get_frame())
            #x, y = image_processing.get_direction(frame, history_frames=15, frame_skip=0, scale_percent=10)
            #log("speed_calculator", abs(y))
            #prefs.set_pref("speed", abs(y))
            
            #log("speed_calculator", prefs.get_pref("speed"))
        except Exception as e:
            log("speed_calculator error - ", e)
            prefs.set_pref("speed", 0)
            time.sleep(1)
    

speed_calculator_thread = threading.Thread(target=speed_calculator)
speed_calculator_thread.start()

#import recorder
#CAMERA_thread = threading.Thread(target=recorder.start_camera_loop)
#CAMERA_thread.start()

from evdev import InputDevice, categorize, ecodes
#creates object 'gamepad' to store the data
#you can call it whatever you like

# TODO : Web interface to pair new device and 
gamepad = InputDevice('/dev/input/event0')

#logs out device info at start
log(gamepad)

shutdown_request = 0


def main():
    #global Camera
    #Camera = c

    global shutdown_request, AUTOPILOT, LAST_DATA
    FIRST_COMMAND = True
    while True:
        try:
            
            LAST_DATA["accel_val"] = 0         # 0 to 100
            LAST_DATA["steering_angle"] = 0    # 0 to 1
            LAST_DATA["speed"] = 0             # 0 to 100

            accel_val = 0
            steering_angle = 0
            
            SPEED_MODE = 1
            
            for event in gamepad.read_loop():

                if FIRST_COMMAND:
                    BUZZER_PATTERN("b b", 0.1)
                    FIRST_COMMAND = False

                #accel_val = 0
                #steering_angle = 0

                if event.code == 16 and event.value==-1 and event.type==3:
                    AUTOPILOT = True
                    BUZZER_PATTERN("b b b", 0.1)
                    LED_PATTERN("B B_")
                
                if event.code == 16 and event.value==0 and event.type==3:
                    if AUTOPILOT:
                        AUTOPILOT = False
                        BUZZER_PATTERN("b b b", 0.1)
                        LED_PATTERN("G")

                rec_toggle = False
                if event.code == 16 and event.value==1 and event.type==3:
                    rec_toggle = True
                
                if event.code == 17 and event.value==1 and event.type==3:
                    log("Compile event triggered")
                    BUZZER_PATTERN("b b", 0.1)
                    if prefs.get_pref("rec")=="0":
                        LED_PATTERN("B B")
                        os.system('python3 compile.py > logs/compile.txt &')
                    else:
                        LED_PATTERN("R R_", 0.25)
                        log("Did not fire compile [currently recording]")
                
                now = time.time()
                if event.code == 17 and event.value==-1 and event.type==3:
                    if shutdown_request==0:
                        log("Shutdown request triggered")
                        shutdown_request = now
                        LED_PATTERN("RB"*4, 0.25)
                
                if event.code == 17 and event.value==0 and event.type==3:
                    if now - shutdown_request < 2 and shutdown_request!=0:    
                        log("Shutdown request dropped")
                        LED_PATTERN("G_")
                        shutdown_request = 0
                
                if shutdown_request!=0:
                    if now - shutdown_request >= 2: # Shutdown button pressed for 2 seconds or more
                        log("SHUTDOWN SIGNAL")
                        LED_PATTERN("R_")
                        BUZZER_PATTERN("b b b b b", 0.1)
                        time.sleep(0.5)
                        os.system("halt")

                if event.type!=0:
                    #filters by event type
                    #log(type(event.code), event.code)
                    if event.code == 1:
                        accel_val = corrected_reading(event.value) * 100
                    elif event.code == 2:
                        steering_angle = corrected_reading(event.value)
                    elif event.code == 304: # A
                        SPEED_MODE = 1
                    elif event.code == 305: # B 
                        SPEED_MODE = 2
                    elif event.code == 307: # X
                        SPEED_MODE = 3
                    elif event.code == 308: # Y
                        SPEED_MODE = 4
                if abs(accel_val) > 25*SPEED_MODE:
                    if accel_val!=0: # To prevent divide by zero error
                        accel_val = 25*SPEED_MODE * accel_val / abs(accel_val)
                    else:
                        accel_val = 25*SPEED_MODE


                loop(accel_val, steering_angle, rec_toggle)
                LAST_DATA["accel_val"] = accel_val
                LAST_DATA["steering_angle"] = steering_angle
                
        except Exception as e:
            log(e)
            if ("No such device" in str(e)):
                log("Bluetooth connection lost")
                # TODO : Reconnect to BT



if __name__ == "__main__":
    #from camera_pi import Camera
    #main(Camera)
    main()