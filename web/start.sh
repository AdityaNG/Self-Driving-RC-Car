python3 web_server.py & LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1.2.0 python3 controls.py &  python3 recorder.py & python3 -m http.server --directory training_data/ 8081 &
