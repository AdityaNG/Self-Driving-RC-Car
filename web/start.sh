python3 web_server.py & LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1.2.0 python3 controls.py & cd training_data; python3 -m http.server
