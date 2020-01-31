import RPi.GPIO as GPIO
from time import sleep

# Forawrd / Backward Pins
in1 = 24
in2 = 23
en = 25

temp1=1

steering_angle = 75

#GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en, GPIO.OUT)
GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.HIGH)

GPIO.output(en, GPIO.HIGH)
sleep(5)
GPIO.output(en, GPIO.LOW)
