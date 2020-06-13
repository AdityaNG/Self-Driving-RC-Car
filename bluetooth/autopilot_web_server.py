from flask import Flask, render_template, Response, request
# Raspberry Pi camera module (requires picamera package, developed by Miguel Grinberg)
from camera_pi import Camera
from urllib.parse import parse_qs
import time
import prefs

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
                        prefs.set_pref(d, params[d][0])
                        prefs.set_pref("last_message", str(time.time()))
                        #print("GOT : ", params)
        except Exception as e:
                PAGE = "{'status': 'not ok', 'error': '" + str(e) + "' }"
        return PAGE

def gen(camera):
        """Video streaming generator function."""
        while True:
                frame = camera.get_frame()
                yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/stream.mjpg')
def video_feed():
        """Video streaming route. Put this in the src attribute of an img tag."""
        return Response(gen(Camera()),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)