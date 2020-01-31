import RPi.GPIO as GPIO
from time import sleep

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

#GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en,GPIO.OUT)
GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)
p=GPIO.PWM(en,50)
p.start(25)

GPIO.setup(tin1,GPIO.OUT)
GPIO.setup(tin2,GPIO.OUT)
GPIO.setup(ten,GPIO.OUT)
GPIO.output(tin1,GPIO.LOW)
GPIO.output(tin2,GPIO.LOW)
tp=GPIO.PWM(ten,50)
tp.start(25)

print("\n")
print("The default speed & direction of motor is LOW & Forward.....")
print("r-run w-forward s-backward l-left d-right e-exit")
print("i-slow o-med p-fast u-stop")
print("\n")

while(1):

    x=input()
    
    if x=='r':
        print("run")
        if(temp1==1):
         GPIO.output(in1,GPIO.HIGH)
         GPIO.output(in2,GPIO.LOW)
         print("forward")
         x='z'
        else:
         GPIO.output(in1,GPIO.LOW)
         GPIO.output(in2,GPIO.HIGH)
         print("backward")
         x='z'


    elif x=='u':
        print("stop")
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.LOW)
        GPIO.output(tin1,GPIO.LOW)
        GPIO.output(tin2,GPIO.LOW)
        x='z'

    elif x=='w':
        print("forward")
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        temp1=1
        x='z'

    elif x=='s':
        print("backward")
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.HIGH)
        temp1=0
        x='z'

    elif x=='a':
        print("left")
        GPIO.output(tin1, GPIO.LOW)
        GPIO.output(tin2, GPIO.HIGH)
        tp.ChangeDutyCycle(steering_angle)

    elif x=='d':
        print("right")
        GPIO.output(tin1, GPIO.HIGH)
        GPIO.output(tin2, GPIO.LOW)
        tp.ChangeDutyCycle(steering_angle)

    elif x=='i':
        print("low")
        p.ChangeDutyCycle(50)
        x='z'

    elif x=='o':
        print("medium")
        p.ChangeDutyCycle(75)
        x='z'

    elif x=='p':
        print("high")
        p.ChangeDutyCycle(100)
        x='z'
     
    
    elif x=='e':
        GPIO.cleanup()
        break
    
    else:
        print("<<<  wrong data  >>>")
        print("please enter the defined data to continue.....")

