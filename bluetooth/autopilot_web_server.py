from flask import Flask, render_template, Response, request
# Raspberry Pi camera module (requires picamera package, developed by Miguel Grinberg)
from camera_pi import Camera
from urllib.parse import parse_qs
import time
import prefs
import json

def log(*a):
        print("[AUTO]", a)

app = Flask(__name__)

@app.route('/')
def index():
        """Video streaming home page."""
        PAGE = "{'status': 'ok'}"
        try:
                params = dict()
                params["accel_val_auto"] = request.args.get('accel_val_auto')
                params["steering_angle_auto"] = request.args.get('steering_angle_auto')
                for d in params:
                        prefs.set_pref(d, params[d])
                        prefs.set_pref("last_message", str(time.time()))
                        log("GOT : ", params)
        except Exception as e:
                PAGE = "{'status': 'not ok', 'error': '" + str(e) + "' }"
        return PAGE


@app.route('/get')
def get():
        """Video streaming home page."""
        PAGE = dict()
        try:
                params = ("accel_val_auto", "steering_angle_auto", "speed")
                for d in params:
                        PAGE[d] = round(float(prefs.get_pref(d)), 5)
                        log("GOT : ", params)
                
                PAGE = json.dumps(PAGE)
        except Exception as e:
                PAGE = "{'status': 'not ok', 'error': '" + str(e) + "' }"
        return PAGE

def gen(camera):
        """Video streaming generator function."""
        while True:
                frame = camera.get_frame()
                yield (b'--frame\r\n'
                b'Content-Type:image/jpeg\r\n'
                b'Content-Length: ' + f"{len(frame)}".encode() + b'\r\n'
                b'\r\n' + frame + b'\r\n')
                #yield (b'--frame\r\n'
                #b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/stream.mjpg')
def video_feed():
        """Video streaming route. Put this in the src attribute of an img tag."""
        return Response(gen(Camera()),
                        mimetype='multipart/x-mixed-replace; boundary=--frame')
                        #mimetype='multipart/x-mixed-replace; boundary=--jpgboundary')


def main():
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)


if __name__ == '__main__':
        main()
        