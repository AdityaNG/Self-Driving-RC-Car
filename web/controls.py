import RPi.GPIO as gpio
import time
import prefs

while True:
	accel_val = int(prefs.get_pref("accel_val"))
	steering_angle = float(prefs.get_pref("steering_angle"))
	print(accel_val, steering_angle, sep=" -- ")
	set_accel(accel_val)
	set_steering(steering_angle)
	time.sleep(0.1)

def init():
	gpio.setwarnings(False)
	gpio.setmode(IO.BCM)
	gpio.setup(19, gpio.OUT)


def set_accel(accel_val):
	pass


def set_steering(steering_angle):
	pass
