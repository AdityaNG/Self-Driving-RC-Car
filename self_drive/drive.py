#parsing command line arguments
#import argparse
#decoding camera images
import base64
#for frametimestamp saving
from datetime import datetime
#reading and writing files
import os
#high level file operations
import shutil
#matrix math
import numpy as np
#real-time server
#import socketio
#concurrent networking 
#import eventlet
#web server gateway interface
#import eventlet.wsgi
#image manipulation
#from PIL import Image
#web framework
#from flask import Flask
#input output
from io import BytesIO

#load our saved model
from keras.models import load_model

#helper class
import utils

import image_processing

import cv2 as cv2
import time
import requests

#initialize our server
#sio = socketio.Server()
#our flask (web) app
#app = Flask(__name__)
#init our model and image array as empty
model = None
prev_image_array = None

#set min/max speed for our autonomous car
MAX_SPEED = 90
MIN_SPEED = 50

#and a speed limit
speed_limit = MAX_SPEED

#registering event handler for the server
def telemetry(data, image):
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
            image = np.asarray(image)       # from PIL image to numpy array
            image = image_processing.process(image)

            cv2.imshow('stream', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                exit()

            image = utils.preprocess(image) # apply the preprocessing
            image = np.array([image])       # the model expects 4D array

            # predict the steering angle for the image
            steering_angle = float(model.predict(image, batch_size=1))
            # lower the throttle as the speed increases
            # if the speed is above the current speed limit, we are on a downhill.
            # make sure we slow down first and then go back to the original max speed.
            global speed_limit
            if speed > speed_limit:
                speed_limit = MIN_SPEED  # slow down
            else:
                speed_limit = MAX_SPEED
            throttle = 1.0 - steering_angle**2 - (speed/speed_limit)**2

            print('{} {} {}'.format(steering_angle, throttle, speed))
            #send_control(steering_angle, throttle)


            prediction["accel_val"] = throttle * 100
            prediction["steering_angle"] = steering_angle
        except Exception as e:
            print(e)

    return (prediction["accel_val"], prediction["steering_angle"])

path_to_model = "/Users/Aditya/Downloads/model-001.h5"

if path_to_model != "":
    #load model
    model = load_model(path_to_model)
    
else:
    print("No Model Found")
    exit()


#IP_ADDRESS = "10.3.141.1"
IP_ADDRESS = "192.168.0.111"

cap = cv2.VideoCapture('http://' + IP_ADDRESS + ':8080/stream.mjpg')

def autopilot_loop():
    result, frame = cap.read()
    if result:

        now = time.time()
        accel_val = 0
        steering_angle = 0
        telemetry_data = dict()
        
        try:
            telemetry_data_response = requests.get("http://" + IP_ADDRESS + ":8080/get")
            telemetry_data = telemetry_data_response.json()
            accel_val = telemetry_data["accel_val_auto"]
            steering_angle = telemetry_data["steering_angle_auto"]
        except Exception as e:
            print("Error parsing telemetry_data_response")
            print(e)
            pass
        
        #print("accel_val", round(accel_val, 3), "\t\tsteering_angle", round(steering_angle, 3), "\t[AUTOPilot]")

        accel_val, steering_angle = telemetry(telemetry_data, frame)

        try:
            send_data_response = requests.get("http://" + IP_ADDRESS + ":8080/?accel_val_auto=" + str(accel_val) + "&steering_angle_auto=" + str(steering_angle))
            #print(send_data_response)
        except Exception as e:
            print("Error parsing send_data_response")
            print(e)
            pass

while True:
	try:
		autopilot_loop()
	except Exception as e:
		print("AUTOPILOT error - ", e)