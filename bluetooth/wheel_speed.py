import RPi.GPIO as GPIO
import time
import prefs
from mpu6050 import mpu6050

MPU_sensor = mpu6050(0x68)

def log(*a):
    print("[WSPS]", a)

def chase_value(goal, chase, chase_factor=0.5):
    return chase + (goal-chase)*chase_factor

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

wheel_speed_pow_pin = 26
GPIO.setup(wheel_speed_pow_pin,GPIO.OUT)
GPIO.output(wheel_speed_pow_pin,GPIO.HIGH)

wheel_speed_data_pin = 19
GPIO.setup(wheel_speed_data_pin,GPIO.IN)
#GPIO.output(wheel_speed_data_pin,GPIO.HIGH)

MPU_delay = 0.05
MPU_last_set = time.time()

wheel_speed_counter = 0
wheel_speed_counter_fault = 100
wheel_speed_counter_last_set = time.time()
wheel_speed_delay = 1.0 # Calculate every 1 seconds
gear_ratio = 1.086956522 # gear_ratio is chosen such that wheel_speed_counter * gear_ratio <= 100

def increment_wheel_speed_counter(channel):
    global wheel_speed_counter
    wheel_speed_counter += 1

GPIO.add_event_detect(wheel_speed_data_pin, GPIO.FALLING, callback=increment_wheel_speed_counter, bouncetime=45)  

def speed_calculator():
    global wheel_speed_counter, wheel_speed_counter_last_set, wheel_speed_delay
    global MPU_last_set, MPU_delay, MPU_sensor

    gyroscope_data_old = {'x':0, 'y':0, 'z': 0}

    prefs.set_pref("speed", 0)
    #time.sleep(10) 
    while True:
        try:
            now = time.time()
            
            #reading = GPIO.input(wheel_speed_data_pin)  
            #if reading:
                #wheel_speed_counter += 1
                #while GPIO.input(wheel_speed_data_pin) == 1:
                    #time.sleep(0.01)
                    #pass # Wait for the sensor to read 0 again before reading the next 1
            
            
            if abs(now - wheel_speed_counter_last_set)>=wheel_speed_delay:
                if wheel_speed_counter>wheel_speed_counter_fault:
                    log("speed_calculator FAULT")
                    prefs.set_pref("speed", 0)
                    prefs.set_pref("rpm", 0)
                else:
                    #log("speed_calculator", reading)

                    speed = float(prefs.get_pref("speed"))
                    rpm = float(wheel_speed_counter) / wheel_speed_delay * 60
                    #accel_val = float(prefs.get_pref("accel_val"))
                    if (wheel_speed_counter!=0):
                        speed = chase_value(wheel_speed_counter * gear_ratio, speed, 0.75)
                    else:
                        speed = 0
                    
                    prefs.set_pref("speed", abs(speed))
                    prefs.set_pref("rpm", abs(int(rpm)))

                    log("speed_calculator", speed, wheel_speed_counter*gear_ratio, wheel_speed_counter)

                wheel_speed_counter_last_set = now
                wheel_speed_counter = 0

            if abs(now - MPU_last_set)>=MPU_delay:
                accelerometer_data = MPU_sensor.get_accel_data()
                gyroscope_data = MPU_sensor.get_gyro_data()

                tmp = gyroscope_data

                for k in gyroscope_data:
                    gyroscope_data[k] = chase_value(gyroscope_data[k], gyroscope_data_old[k], 0.5)
                
                gyroscope_data_old = tmp

                prefs.set_pref("accelerometer_data", str(accelerometer_data))
                prefs.set_pref("gyroscope_data", str(gyroscope_data))
                MPU_last_set = now
            #global Camera
            #frame = decodeImage(Camera().get_frame())
            #x, y = image_processing.get_direction(frame, history_frames=15, frame_skip=0, scale_percent=10)
            #log("speed_calculator", abs(y))
            #prefs.set_pref("speed", abs(y))
            
            #log("speed_calculator", prefs.get_pref("speed"))
        except Exception as e:
            log("speed_calculator error - ", e)
            prefs.set_pref("speed", 0)
            time.sleep(1)
    

def main():
    speed_calculator()

if __name__ == "__main__":
    #from camera_pi import Camera
    #main(Camera)
    main()
#speed_calculator_thread = threading.Thread(target=speed_calculator)
#speed_calculator_thread.start()