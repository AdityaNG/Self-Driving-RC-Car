# sudo modprobe bcm2835-v4l2

python3 controller.py   > logs/controller.txt &
python3 autopilot_web_server.py > logs/autopilot_web_server.txt &
python3 recorder.py     > logs/recorder.txt &
cd training_data; 
#python3 -m http.server > ../logs/recorder.txt &