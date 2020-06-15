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

def log(*a):
	print("[RECO]", a)


def last_command_time():
	return min(( float(prefs.get_pref_time("accel_val")), float(prefs.get_pref_time("steering_angle"))))


time.sleep(10) # Wait 10 seconds for server to start up
cap = cv2.VideoCapture('http://localhost:8080/stream.mjpg')

steering_angle = 75

global tank_controls
tank_controls = False;


# PICS steering_angle speed throttle brakes
def loop():
	result, frame = cap.read()
	global tank_controls
	now = time.time()

	accel_val = 0
	steering_angle = 0
	rec = prefs.get_pref("rec")
	av = prefs.get_pref("accel_val")
	sa = prefs.get_pref("steering_angle")
	try:
		accel_val = float(av)
		steering_angle = float(sa)
		#log("accel_val=", av, "\tsteering_angle=", sa)
	except:
		#log("accel_val=", av, "\tsteering_angle=", sa, "[ERROR]")
		pass

	if now-last_command_time()<15: # Stop recording if idle for more than 15 seconds
		filename = os.path.join(os.getcwd(), 'training_data', rec, 'data.csv')
		log("RECORDING TO ", filename)
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
		
		cv2.imwrite(imagefile, frame)

		speed = accel_val # TODO : Calculate speed using wheel speed
		throttle = 0
		brakes = 0
		if accel_val>0:
			throttle = accel_val
		else:
			brakes = accel_val

		#myCsvRow = ",".join(list(map(str, [data_imagefile, steering_angle, speed, throttle, brakes])))
		myCsvRow = ",".join(list(map(str, [data_imagefile, steering_angle, accel_val])))
		log('Append Row : ', myCsvRow)

		with open(filename, 'a') as fd: # Append to file
			fd.write(myCsvRow + '\n')

def main():
	while True:
		try:
			if prefs.get_pref("rec")!="0":
				loop()
		except Exception as e:
			log("RECORDER - ", e)

if __name__ == "__main__":
    main()