#  LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1.2.0 python3 controls.py

import RPi.GPIO as GPIO
import time
import prefs
import os
import errno
import cv2 as cv2
import shutil
#import picamera

#camera = picamera.PiCamera()
#camera.capture('example.jpg')

# time.sleep(10) # Wait 10 seconds for server to start up


#cap = cv2.VideoCapture('http://localhost:8080/stream.mjpg')

steering_angle = 75

global tank_controls
tank_controls = False;


def compile_data():
	os.system('python3 compile.py &')

compile_data()
last_compile = time.time()
# PICS steering_angle speed throttle brakes
def loop(frame):
	global last_compile
	global tank_controls
	now = time.time()
	if now-last_compile>60*10: # Recompile training data every 10 minutes
		compile_data()

	rec = prefs.get_pref("rec")
	accel_val = int(prefs.get_pref("accel_val"))
	steering_angle = float(prefs.get_pref("steering_angle"))
	#print(accel_val, steering_angle, sep=" -- ")
	#set_accel(accel_val)

	# TODO use get_pref_time
	#if rec != '0' and time.time()-float(prefs.get_pref("last_message"))<15: # Last command issued within 15 seconds
	# Last command issued within 15 seconds
	if rec != '0' and rec!="" and (now-float(prefs.get_pref_time("accel_val"))<15 or now-float(prefs.get_pref_time("steering_angle"))<15): 
	#if False:
		# print("REC...")
		filename = os.path.join(os.getcwd(), 'training_data', rec, 'data.csv')
		if not os.path.exists(os.path.dirname(filename)):
			try:
				os.makedirs(os.path.dirname(filename))
				os.mkdir(os.path.join(os.path.dirname(filename), 'images'))
			except OSError as exc: # Guard against race condition
				if exc.errno != errno.EEXIST:
					raise


		time_now = str(now)
		imagefile = os.path.join(os.path.dirname(filename), 'images', time_now + ".jpg")
		data_imagefile = os.path.join('images', time_now + ".jpg")
		#camera.capture(imagefile)
		#result, frame = cap.read()
		result = True # Use 
		if result:
			# print("Got Image")
			cv2.imwrite(imagefile, frame)

			speed = accel_val # TODO : Calculate speed
			throttle = 0
			brakes = 0

			if accel_val>0:
				throttle = accel_val
			else:
				brakes = accel_val

			myCsvRow = ",".join(list(map(str, [data_imagefile, steering_angle, speed, throttle, brakes])))
			# print('Append Row : ', myCsvRow)
			#myCsvRow = " ".join(list(map(str, [imagefile, steering_angle, speed, accel_val])))
			with open(filename, 'a') as fd: # Append to file
				fd.write(myCsvRow + '\n')
		else:
			print("REC ERROR - COULD NOT GET IMAGE")
	#time.sleep(0.1)


# import the necessary packages
import picamera
import io
#from picamera.array import PiRGBArray
#from picamera import PiCamera
import time
from numpy.lib.npyio import NpzFile 
#import cv2
# initialize the camera and grab a reference to the raw camera capture
#camera = PiCamera()
#camera.resolution = (640, 480)
#camera.framerate = 32
#rawCapture = PiRGBArray(camera, size=(640, 480))
# allow the camera to warmup
time.sleep(0.1)
# capture frames from the camera
with picamera.PiCamera() as camera:
	stream = io.BytesIO()
	for frame in camera.capture_continuous(stream, format='jpeg'):
		stream.truncate()
		stream.seek(0)
		try:
			ret = NpzFile(stream, own_fid=True, allow_pickle=True)  
			print(ret.files)
			print(ret)
			print(dir(ret))
			loop(stream)
		except Exception as e:
			print(e)
