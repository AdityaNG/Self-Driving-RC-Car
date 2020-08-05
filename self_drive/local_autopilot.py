
import base64
from datetime import datetime
import os
import shutil
import numpy as np
import math
from io import BytesIO

import time
#helper class
import utils

import image_processing

import cv2 as cv2
import time
import requests

import sys
sys.path.append("../bluetooth")
import prefs

from simple_pid import PID
pid = PID(1, 0.1, 3, setpoint=44.43)
#pid.output_limits = (0, 100)    
pid.output_limits = (-5, 75)    


def log(*a):
    print("[CVAT]", a)
    pass

def sigmoid(x):
    return 1 / (1 + math.exp(-x))


Camera = 0

#initialize our server
#sio = socketio.Server()
#our flask (web) app
#app = Flask(__name__)
#init our model and image array as empty
model = None
prev_image_array = None

#set min/max speed for our autonomous car
MAX_SPEED = 65
MIN_SPEED = 35

#and a speed limit
speed_limit = MAX_SPEED

OLD_FRAME = False
#registering event handler for the server
def telemetry(data, image=False):
    global pid
    prediction = dict()
    prediction["accel_val_auto"] = 0         # 0 to 100
    prediction["steering_angle_auto"] = 0    # 0 to 1
    if data:
        # The current steering angle of the car
        steering_angle = float(data["steering_angle_auto"])
        # The current throttle of the car, how hard to push peddle
        throttle = float(data["accel_val_auto"])
        # The current speed of the car
        speed = float(data["speed"])
        # The current image from the center camera of the car
        #image = Image.open(BytesIO(base64.b64decode(data["image"])))
        try:
            if type(image)!=type(False):
                image = np.asarray(image)       # from PIL image to numpy array
                image = image_processing.process(image)

            #cv2.imshow('stream', image)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
                #exit()

            #image = utils.preprocess(image) # apply the preprocessing
            #image = np.array([image])       # the model expects 4D array

            # predict the steering angle for the image
            #steering_angle = float(model.predict(image, batch_size=1))
            # TODO : predict steering angle
            steering_angle = 0
            
            # lower the throttle as the speed increases
            # if the speed is above the current speed limit, we are on a downhill.
            # make sure we slow down first and then go back to the original max speed.
            global speed_limit
            if speed > speed_limit:
                speed_limit = MIN_SPEED  # slow down
            else:
                speed_limit = MAX_SPEED
            
            #throttle = 1.0 - steering_angle**2 - (speed/speed_limit)**2

            #throttle = throttle * 100

            throttle = pid(speed)

            #if throttle>100:
            #    throttle = 100
            
            #if throttle>25:
            #    throttle = 25

            #if throttle<0:
            #    throttle = 0

            
            #pid.setpoint = 40
            

            steering_angle = 2*sigmoid(10* steering_angle) -1

            if 1 - abs(steering_angle) < 0.3:
                #log('{} {} {} STEER'.format(steering_angle, throttle, speed))
                pass
            else:
                #log('{} {} {}'.format(steering_angle, throttle, speed))
                pass

            prediction["accel_val"] = throttle
            prediction["steering_angle"] = steering_angle
        except Exception as e:
            log(e)

    return (prediction["accel_val"], prediction["steering_angle"])


#IP_ADDRESS = "10.3.141.1"
#IP_ADDRESS = "192.168.0.111"
IP_ADDRESS = "localhost"

# cap = cv2.VideoCapture('http://' + IP_ADDRESS + ':8080/stream.mjpg')

def decodeImage(image_bytes):
    return cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)


def autopilot_loop():
    frame = decodeImage(Camera().get_frame())
    if frame.any():
        now = time.time()

        telemetry_data = dict()
        telemetry_data["accel_val_auto"] = 0.0
        telemetry_data["steering_angle_auto"] = 0.0
        telemetry_data["speed"] = 0.0
        try:
            telemetry_data["accel_val_auto"] = float(prefs.get_pref("accel_val_auto"))
        except:
            prefs.set_pref("accel_val_auto", 0.0)
        try:
            telemetry_data["steering_angle_auto"] = float(prefs.get_pref("steering_angle_auto"))
        except:
            prefs.set_pref("steering_angle_auto", 0.0)
        try:
            telemetry_data["speed"] = float(prefs.get_pref("speed"))
        except:
            prefs.set_pref("speed", 0.0)

        #telemetry_data["speed"] = float(abs(y))
        
        #log("accel_val", round(telemetry_data["accel_val_auto"], 3), "steering_angle", round(telemetry_data["steering_angle_auto"], 3), "[AUTOPILOT]")

        accel_val, steering_angle = telemetry(telemetry_data, frame)

        steering_angle = 0

        prefs.set_pref("accel_val_auto", accel_val)
        prefs.set_pref("steering_angle_auto", steering_angle)

def throttle_loop():
    #time.sleep(1)
    now = time.time()

    telemetry_data = dict()
    telemetry_data["accel_val_auto"] = 0.0
    telemetry_data["steering_angle_auto"] = 0.0
    telemetry_data["speed"] = 0.0
    try:
        telemetry_data["accel_val_auto"] = float(prefs.get_pref("accel_val_auto"))
    except:
        pass
    try:
        telemetry_data["steering_angle_auto"] = float(prefs.get_pref("steering_angle_auto"))
    except:
        pass
    try:
        telemetry_data["speed"] = float(prefs.get_pref("speed"))
    except:
        pass

        #telemetry_data["speed"] = float(abs(y))
        
        #log("accel_val", round(telemetry_data["accel_val_auto"], 3), "steering_angle", round(telemetry_data["steering_angle_auto"], 3), "[AUTOPILOT]")

    accel_val, steering_angle = telemetry(telemetry_data)

    print(telemetry_data["speed"], "\t -> \t", accel_val)
    prefs.set_pref("accel_val_auto", accel_val)

def main(c):
    global Camera
    Camera = c
    while True:
        try:
            now = time.time()
            if prefs.get_pref("AUTOPILOT")=="1":# and abs(now - prefs.get_pref_time("AUTOPILOT")) < 1:
                #autopilot_loop()
                for i in range(1000):
                    throttle_loop()
            else:
                time.sleep(1)
        except Exception as e:
            log("AUTOPILOT error - ", e)

if __name__ == '__main__':
    from camera_pi import Camera
    main(Camera)
