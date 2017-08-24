#!/usr/bin/env python3
import base64
import concurrent.futures
import cv2
import numpy as np
import os
import pyaudio
import pynmea2
import requests
import scipy.misc
from socketIO_client import SocketIO
import serial
import time

SERVER_IP = 'localhost'  # Enter public IP of web server here
SERVER_PORT = 5000  # Enter the port that web server is using


class ultimate_gps():
    def __init__(self):
        self.connect()
        self.data_gen = self._data_generator()

    def connect(self):
        gps_uart = serial.Serial()
        gps_uart.baudrate = 9600
        gps_uart.port = '/dev/serial0'
        gps_uart.timeout = 2
        gps_uart.open()
        self._gps_uart = gps_uart

    def reconnect(self):
        self.close()
        self.connect()
        self.data_gen = self._data_generator()

    def close(self):
        self._gps_uart.close()

    def _data_generator(self):
        '''Yield a tuple containing raw nmea data and parsed nmea data.'''
        while True:
            if self._gps_uart.inWaiting():
                recv = self._gps_uart.readline().decode()
                if '$GPGGA' in recv:
                    nmea_data = pynmea2.parse(recv)
                    if nmea_data.is_valid:
                        yield recv, nmea_data
                    else:
                        time.sleep(1)
            else:
                time.sleep(0.5)


def create_logfile(logfile='gpslog.csv'):
    if not os.path.isfile('gpslog.csv'):
        with open('gpslog.csv', 'w+') as gpslog:
            gpslog.write('timestamp, longitude, latitude\n')
    else:
        print('''Logfile: 'gpslog.csv' already exists.''')


def log_data(recv_parsed):
    with open('gpslog.csv', 'a') as gpslog:
        gpslog.write('{}, {}, {}\n'.format(recv_parsed.timestamp,
                                           recv_parsed.longitude,
                                           recv_parsed.latitude))


def emit_frame(cam):
    frame = cam.read()[1]
    frame_sm = scipy.misc.imresize(frame, 30)
    enc_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
    frame_enc = cv2.imencode('.jpeg', frame_sm, enc_param)[1].tostring()
    frame_b64 = base64.encodebytes(frame_enc)
    socketIO.emit('frame', frame_b64.decode())


def frame_loop(sleep_time=1/100):
    cam = cv2.VideoCapture(0)
    while True:
        try:
            emit_frame(cam)
        except Exception as err:
            print(err)
        time.sleep(sleep_time)


def emit_gps(recv, recv_parsed):
    try:
        socketIO.emit('gps', recv)
        socketIO.emit('coordinates', recv_parsed.latitude,
                      recv_parsed.longitude)
    except Exception as err:
        print('emit_gps', err)


def gps_loop():
    while True:
        try:
            recv, recv_parsed = next(gps.data_gen)
        except Exception as err:
            print('gps_loop', err.__class__.__name__, err)
            gps.reconnect()
        else:
            log_data(recv_parsed)
            emit_gps(recv, recv_parsed)


def audio_callback(in_data, frame_count, time_info, status):
    audio_data = np.fromstring(in_data, dtype='int8').tolist()
    print(len(in_data))
    try:
        socketIO.emit('audio', audio_data)
    except Exception as err:
        print('emit_audio', err)
    return None, pyaudio.paContinue


def audio_loop():
    while True:
        pya = pyaudio.PyAudio()
        chunk_length = 1
        audio_stream = pya.open(format=pyaudio.paInt8,
                                channels=1,
                                rate=44100,
                                input=True,
                                frames_per_buffer=int(44100 * chunk_length),
                                stream_callback=audio_callback)
        audio_stream.start_stream()
        while audio_stream.is_active():
            time.sleep(0.1)
        audio_stream.stop_stream()
        audio_stream.close()
        pya.terminate()


def wait_for_connection():
    first_attempt = True
    while True:
        try:
            resp = requests.get(('http://' + str(SERVER_IP) + ':' +
                                 str(SERVER_PORT) + '/'), timeout=5)
        except:
            time.sleep(1)
            if first_attempt:
                print('not connected to internet')
                first_attempt = False
        else:
            break
    print('connected to internet')


def maintain_connection():
    global connected, socketIO
    try:
        resp = requests.get(('http://' + str(SERVER_IP) + ':' +
                             str(SERVER_PORT) + '/'), timeout=5)
    except:
        print('lost connection')
        connected = False
        wait_for_connection()
        socketIO.close()
        socketIO = SocketIO(SERVER_IP, SERVER_PORT)
    else:
        connected = True


if __name__ == '__main__':
    gps = ultimate_gps()
    wait_for_connection()
    connected = True
    socketIO = SocketIO(SERVER_IP, SERVER_PORT, timeout=2)
    create_logfile()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(gps_loop)
        executor.submit(frame_loop)
        executor.submit(audio_loop)
        while True:
            maintain_connection()
            time.sleep(5)
