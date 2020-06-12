sudo modprobe bcm2835-v4l2

python3 controller.py &
python3 recorder.py &
cd training_data; python3 -m http.server &