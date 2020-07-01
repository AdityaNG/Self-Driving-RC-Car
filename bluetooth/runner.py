"""
# sudo modprobe bcm2835-v4l2

# python3 controller.py   > logs/controller.txt &
# python3 autopilot_web_server.py > logs/autopilot_web_server.txt &
# python3 recorder.py     > logs/recorder.txt &
cd training_data; 
#python3 -m http.server > ../logs/webserver.txt &
"""

import threading
import time
import sys

from camera_pi import Camera

import controller
from controller import bluetooth_connected, connect_bluetooth_loop
import autopilot_web_server
import recorder

sys.path.append("../self_drive")
import local_autopilot

THREADS = []

THREADS.append(threading.Thread(target=controller.main, args=(Camera, ) ))
THREADS[0].setName("Controller")

THREADS.append(threading.Thread(target=autopilot_web_server.main, args=(Camera, ) ))
THREADS[1].setName("Autopilot Webserver")

THREADS.append(threading.Thread(target=recorder.main))
THREADS[2].setName("Recorder")

THREADS.append(threading.Thread(target=local_autopilot.main, args=(Camera, ) ))
THREADS[3].setName("Local Autopilot")

#THREADS.append(threading.Thread(target=controller.main))
#THREADS.append(threading.Thread(target=controller.main))

def log(*a):
    print("[THRD]", a)


def launch_all():
    for t in THREADS:
        t.start()
        log(t.name, " Started")
        if t.name=="Autopilot Webserver":
            time.sleep(10)


def loop():
    for t in THREADS:
        if not t.is_alive():
            log(t.name, " - Died")

def main():
    if not bluetooth_connected():
        connect_bluetooth_loop()

    launch_all()
    while True:
        try:
            loop()    
        except Exception as e:
            log("Runner error - ", e)
            
        time.sleep(5)

if __name__ == "__main__":
    main()

