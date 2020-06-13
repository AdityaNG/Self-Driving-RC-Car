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
    prediction["accel_val"] = 0         # 0 to 100
    prediction["steering_angle"] = 0    # 0 to 1
    if data:
        # The current steering angle of the car
        steering_angle = float(data["steering_angle"])
        # The current throttle of the car, how hard to push peddle
        throttle = float(data["accel_val"])
        # The current speed of the car
        speed = float(data["speed"])
        # The current image from the center camera of the car
        #image = Image.open(BytesIO(base64.b64decode(data["image"])))
        try:
            image = np.asarray(image)       # from PIL image to numpy array
            image = image_processing.process(image_processing)
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
            prediction["accel_val"] = throttle
            prediction["steering_angle"] = steering_angle
        except Exception as e:
            print(e)

    return (prediction["accel_val"], prediction["steering_angle"])

path_to_model = "/root/models/model-001.1592029795.5388622.h5"

if path_to_model != "":
    #load model
    model = load_model(path_to_model)
    
else:
    print("No Model Found")