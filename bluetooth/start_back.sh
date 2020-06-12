python3 controller.py   > logs/controller.txt &
python3 recorder.py     > logs/recorder.txt &
cd training_data; 
python3 -m http.server  > logs/recorder.txt &