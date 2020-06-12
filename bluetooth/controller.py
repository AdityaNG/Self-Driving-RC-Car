#  LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1.2.0 python3 controls.py

import RPi.GPIO as GPIO
import time
import prefs
import os
import errno
import shutil

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

RED_PIN = 10
GREEN_PIN = 11
BLUE_PIN = 9

GPIO.setup(RED_PIN,GPIO.OUT)
GPIO.setup(GREEN_PIN,GPIO.OUT)
GPIO.setup(BLUE_PIN,GPIO.OUT)

import threading

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

# Bluetooth connect 
while "event0" not in os.listdir("/dev/input/"):
    LED_PATTERN("B B B B B_", 0.25)
    os.system('./bluetooth_connect.sh')
    time.sleep(10) # Wait

LED_PATTERN("B B G G G G G_", 0.25)


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
            #print(out)
            last_out = out
        return

    tf = (steering_angle + 1)
    p.ChangeDutyCycle(abs(accel_val * tf/2.0))
    tp.ChangeDutyCycle(abs(accel_val * (1 - abs(tf)/2.0) * 2))
    
    out = "p" + str(abs(accel_val * tf)) + "; tp" + str(abs(accel_val * (1 - abs(tf))))
    if out!=last_out:
        #print(out)
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
def loop(accel_val, steering_angle, rec_toggle=False):
    global tank_controls

    if rec_toggle:
        if prefs.get_pref("rec")=="0":
            LED_PATTERN("R R_")
            print("Rec ON")
            prefs.set_pref("rec", str(time.time()))
        else:
            LED_PATTERN("R R")
            print("Rec OFF")
            prefs.set_pref("rec", "0")

    print("accel_val", accel_val)
    print("steering_angle", steering_angle)

    av = str(accel_val)
    prefs.set_pref("accel_val", av)
    
    sa = str(steering_angle)
    prefs.set_pref("steering_angle", sa)

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

# TODO : Web interface to pair new device and 
gamepad = InputDevice('/dev/input/event0')

#prints out device info at start
print(gamepad)

shutdown_request = 0

while True:
    try:
        accel_val = 0
        steering_angle = 0
        
        SPEED_MODE = 1

        now = time.time()
            if shutdown_request!=0:
                if now - shutdown_request >= 2: # Shutdown button pressed for 2 seconds or more
                    print("SHUTDOWN SIGNAL")
                    LED_PATTERN("R_")
                    time.sleep(0.5)
                    #os.system("halt")

        for event in gamepad.read_loop():
            #accel_val = 0
            #steering_angle = 0
            rec_toggle = False
            if event.code == 16 and event.value==1 and event.type==3:
                rec_toggle = True
            
            if event.code == 17 and event.value==1 and event.type==3:
                print("Compile event triggered")
                if prefs.get_pref("rec")=="0":
                    LED_PATTERN("B B")
                    os.system('python3 compile.py > logs/compile.txt &')
                else:
                    LED_PATTERN("R R_", 0.25)
                    print("Did not fire compile [currently recording]")
            
            
            if event.code == 17 and event.value==-1 and event.type==3:
                if shutdown_request==0:
                    print("Shutdown request triggered")
                    shutdown_request = now
                    LED_PATTERN("RB"*4, 0.25)
            
            if event.code == 17 and event.value==0 and event.type==3:
                if now - shutdown_request < 2 and shutdown_request!=0:    
                    print("Shutdown request dropped")
                    LED_PATTERN("G_")
                    shutdown_request = 0
            

            if event.type!=0:
                #filters by event type
                #print(type(event.code), event.code)
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
    except Exception as e:
        pass
        print(e)
