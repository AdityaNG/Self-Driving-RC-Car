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

time.sleep(10) # Wait 10 seconds for server to start up
cap = cv2.VideoCapture('http://localhost:8080/stream.mjpg')

# Forawrd / Backward Pins
in1 = 24
in2 = 23
en = 25

temp1=1

# Left / Right Pins
tin1 = 17
tin2 = 27
ten = 22

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
tank_controls = True;

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
		GPIO.output(tin1,GPIO.LOW)
		GPIO.output(tin2,GPIO.HIGH)
	elif accel_val<0:
		# Backwards
		GPIO.output(in1,GPIO.HIGH)
		GPIO.output(in2,GPIO.LOW)
		GPIO.output(tin1,GPIO.HIGH)
		GPIO.output(tin2,GPIO.LOW)
	else:
		if steering_angle>0:
			# Pure Left
			GPIO.output(in1,GPIO.LOW)
			GPIO.output(in2,GPIO.HIGH)
			GPIO.output(tin1,GPIO.HIGH)
			GPIO.output(tin2,GPIO.LOW)
		else:
			# Pure Right
			GPIO.output(in1,GPIO.HIGH)
			GPIO.output(in2,GPIO.LOW)
			GPIO.output(tin1,GPIO.LOW)
			GPIO.output(tin2,GPIO.HIGH)
		p.ChangeDutyCycle(abs(steering_angle))
		tp.ChangeDutyCycle(abs(steering_angle))

		out = "p" + str(abs(steering_angle)) + "; tp" + str(abs(steering_angle))
		if out!=last_out:
			print(out)
			last_out = out
		return
	tf = steering_angle + 1
	p.ChangeDutyCycle(abs(accel_val * tf))
	tp.ChangeDutyCycle(abs(accel_val * (1 - abs(tf))))
	
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

def compile_data():
	os.system('python3 compile.py &')

compile_data()
last_compile = time.time()
# PICS steering_angle speed throttle brakes
def loop():
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
	if tank_controls:
		tank_mover(steering_angle, accel_val)
	else:
		set_accel(accel_val)
		set_steering(steering_angle)

#	if rec != '0' and time.time()-float(prefs.get_pref("last_message"))<15: # Last command issued within 15 seconds
	if False:
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
