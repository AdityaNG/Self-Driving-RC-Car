import io
try:
    import picamera
except:
    print("ModuleNotFoundError: No module named 'picamera'")
import logging
import socketserver
from threading import Condition
from http import server
from os import curdir, sep
from urllib.parse import parse_qs
import time
import os

import prefs

#f = open('index.html')
#PAGE=f.read()


class StreamingOutput(object):
        def __init__(self):
                self.frame = None
                self.buffer = io.BytesIO()
                self.condition = Condition()

        def write(self, buf):
                if buf.startswith(b'\xff\xd8'):
                        # New frame, copy the existing buffer's content and notify all
                        # clients it's available
                        self.buffer.truncate()
                        with self.condition:
                                self.frame = self.buffer.getvalue()
                                self.condition.notify_all()
                        self.buffer.seek(0)
                return self.buffer.write(buf)


class StreamingHandler(server.BaseHTTPRequestHandler):
        def do_GET(self):
                global params
                if "/?" in self.path:
                        
                        PAGE = "{'status': 'ok'}"
                        try:
                                params = parse_qs(self.path[2:])
                                for d in params:
                                    prefs.set_pref(d, params[d][0])
                                prefs.set_pref("last_message", str(time.time()))
                                #print("GOT : ", params)
                        except Exception as e:
                                PAGE = "{'status': 'not ok', 'error': '" + str(e) + "' }"
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/json')
                        content = PAGE.encode('utf-8')
                        self.send_header('Content-Length', len(content))
                        self.end_headers()
                        self.wfile.write(content)
                elif "/get" in self.path:
                        PAGE = "{'status': 'Searching'}"
                        try:
                                req = self.path.split("/")[2]
                                #print(req)
                                

                                PAGE = prefs.get_pref(req)
                                if PAGE=="":
                                    PAGE = "NULL"
                                
                                #print("GOT : ", {req: PAGE})
                                #PAGE = str(params)
                        except Exception as e:
                                PAGE = "{'status': 'not ok', 'error': '" + str(e) + "' }"
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/json')
                        content = PAGE.encode('utf-8')
                        self.send_header('Content-Length', len(content))
                        self.end_headers()
                        self.wfile.write(content)
                elif self.path == '/':
                        self.send_response(301)
                        self.send_header('Location', '/index.html')
                        self.end_headers()
                """elif self.path == '/stream.mjpg':
                        self.send_response(200)
                        self.send_header('Age', 0)
                        self.send_header('Cache-Control', 'no-cache, private')
                        self.send_header('Pragma', 'no-cache')
                        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
                        self.end_headers()
                        try:
                                while True:
                                        with output.condition:
                                                output.condition.wait()
                                                frame = output.frame
                                        self.wfile.write(b'--FRAME\r\n')
                                        self.send_header('Content-Type', 'image/jpeg')
                                        self.send_header('Content-Length', len(frame))
                                        self.end_headers()
                                        self.wfile.write(frame)
                                        self.wfile.write(b'\r\n')
                        except Exception as e:
                                logging.warning(
                                        'Removed streaming client %s: %s',
                                        self.client_address, str(e))"""
                else:
                        SERVER_PATH = "web/"
                        try:
                                #print('Opening file : ', self.path[1:])
                                PAGE = ""
                                self.send_response(200)
                                if self.path.endswith('.png'):
                                                #print('Inside IF')
                                                f = open(os.path.join(SERVER_PATH, self.path[1:]) , 'rb')
                                                PAGE = f.read()
                                                self.send_header('Content-Type', 'image/png')
                                                content = PAGE
                                else:
                                                f = open(os.path.join(SERVER_PATH, self.path[1:]), 'r')
                                                PAGE = f.read()
                                                self.send_header('Content-Type', 'text/html')
                                                content = PAGE.encode('utf-8')
                                self.send_header('Content-Length', len(content))
                                self.end_headers()
                                self.wfile.write(content)
                        except Exception as e:
                                self.send_error(404)
                                self.end_headers()
                                print(e)

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
        allow_reuse_address = True
        daemon_threads = True

def main(c):
    try:
        print("Starting Server")
        address = ('', 8080)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()

        

if __name__ == "__main__":
    try:
        with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
            output = StreamingOutput()
            #Uncomment the next line to change your Pi's Camera rotation (in degrees)
            camera.rotation = 180
            camera.start_recording(output, format='mjpeg')
            print("Camera opened, starting server at port 8080")
            main(camera)

    except:
        print("Camera Error")
        main()