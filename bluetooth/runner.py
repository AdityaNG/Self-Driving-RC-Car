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

import controller
import autopilot_web_server
import recorder

THREADS = []

THREADS.append(threading.Thread(target=controller.main))
THREADS.append(threading.Thread(target=autopilot_web_server.main))
THREADS.append(threading.Thread(target=recorder.main))

#THREADS.append(threading.Thread(target=controller.main))
#THREADS.append(threading.Thread(target=controller.main))

def launch_all():
    for t in THREADS:
        t.start()
        print("[Thread] ", t.name, " - Started")


def loop():
    for t in THREADS:
        if not t.is_alive():
            print("[Thread] ", t.name, " - Died")

def main():
    launch_all()
    while True:
        try:
            loop()    
        except Exception as e:
            print("RECORDER - ", e)
            
        time.sleep(5)

if __name__ == "__main__":
    main()

