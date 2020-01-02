#  LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1.2.0 python3 controls.py

import RPi.GPIO as gpio
import time
import prefs
import os
import errno
import cv2 as cv2
import shutil
#import picamera

#camera = picamera.PiCamera()
#camera.capture('example.jpg')
cap = cv2.VideoCapture('http://localhost:8000/stream.mjpg')

def init():
	gpio.setwarnings(False)
	gpio.setmode(IO.BCM)
	gpio.setup(19, gpio.OUT)


def set_accel(accel_val):
	pass


def set_steering(steering_angle):
	pass


def compile_training_data():
	print('Compiling Training Data')
	td = os.path.join(os.getcwd(), 'training_data')
	folders = [ name for name in os.listdir(td) if os.path.isdir(os.path.join(td, name)) ]
	for i in folders:
		print("\t Compiling : ",i)
		c_dir = os.path.join(os.getcwd(), 'training_data', i)
		shutil.make_archive(c_dir, 'zip', c_dir)


compile_training_data()
# PICS steering_angle speed throttle brakes
def loop():
	rec = prefs.get_pref("rec")
	accel_val = int(prefs.get_pref("accel_val"))
	steering_angle = float(prefs.get_pref("steering_angle"))
	#print(accel_val, steering_angle, sep=" -- ")
	set_accel(accel_val)
	set_steering(steering_angle)

	if rec != '0' and time.time()-float(prefs.get_pref("last_message"))<15: # Last command issued within 15 seconds
		print("REC...")
		filename = os.path.join(os.getcwd(), 'training_data', rec, 'data.csv')
		if not os.path.exists(os.path.dirname(filename)):
			try:
				os.makedirs(os.path.dirname(filename))
				os.mkdir(os.path.join(os.path.dirname(filename), 'images'))
			except OSError as exc: # Guard against race condition
				if exc.errno != errno.EEXIST:
					raise

		imagefile = os.path.join(os.path.dirname(filename), 'images', str(time.time()) + ".jpg")
		#camera.capture(imagefile)
		result, frame = cap.read()

		if result:
			print("Got Image")
			cv2.imwrite(imagefile, frame)

			speed = accel_val # TODO : Calculate speed
			throttle = 0
			brakes = 0

			if accel_val>0:
				throttle = accel_val
			else:
				brakes = accel_val

			myCsvRow = ",".join(list(map(str, [imagefile, steering_angle, speed, throttle, brakes])))
			print('Append Row : ', myCsvRow)
			#myCsvRow = " ".join(list(map(str, [imagefile, steering_angle, speed, accel_val])))
			with open(filename, 'a') as fd: # Append to file
    				fd.write(myCsvRow + '\n')
		else:
			print("COULD NOT GET IMAGE")
	#time.sleep(0.1)


while True:
	try:
		loop()
	except Exception as e:
		print(e)
