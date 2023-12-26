from flask import Flask, render_template, Response
# from flask_socketio import SocketIO, send, emit
from camera import camera
import json
import cv2

app = Flask(__name__)
# socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def hello():
    return render_template('sample.html')

@app.route('/logs')
def getLogs():
    print("logs....")

def gen(cm):
    while True:
        frame = cm.get_frame()

        if frame is not None:
            yield (b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame.tobytes() + b"\r\n")
        else:
            print("frame is none")

@app.route("/video_feed")
def video_feed():
    return Response(gen(camera.Camera()),
            mimetype="multipart/x-mixed-replace; boundary=frame")

# @socketio.on('connect')
# def connect(auth):
#     print("connect!!!!")
#     print(auth)
#     global user_count, text
#     user_count += 1
#     emit('count_update', {'user_count': user_count}, broadcast=True)
#     emit('text_update', {'text': text})

if __name__ == "__main__":
    app.run(debug=False, port=8888, threaded=True)  