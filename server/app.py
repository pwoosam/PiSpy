import socketio
import eventlet
from flask import Flask, render_template

SERVER_IP = 'localhost'  # Enter local IP of web server here
SERVER_PORT = 5000  # Enter the local port that web server is using

sio = socketio.Server()
app = Flask(__name__)


@app.route('/')
def index():
    '''Render index.'''
    return render_template('index.html')


@app.route('/map.html')
def gps_map():
    '''Render gps coordinates on map.'''
    return render_template('map.html')


@app.route('/frame.html')
def video_stream():
    '''Render frames for video stream.'''
    return render_template('frame.html')


@sio.on('connect')
def connect(sid, environ):
    print('connect ', sid)


@sio.on('gps')
def receive_gps(sid, gps_data):
    pass


@sio.on('coordinates')
def receive_gps_coordinates(sid, latitude, longitude):
    '''Broadcast gps coordinates on 'updatemap' channel.'''
    sio.emit('updatemap', data={'lat': latitude, 'lng': longitude})


@sio.on('frame')
def receive_frame(sid, frame_data):
    '''Broadcast frame on 'frame' channel.'''
    sio.emit('frame', data=frame_data)


@sio.on('audio')
def receive_audio(sid, audio_data):
    '''Broadcast audio on 'audio' channel.'''
    pass


@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)


if __name__ == '__main__':
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen((SERVER_IP, SERVER_PORT)), app)
