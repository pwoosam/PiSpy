#!/usr/bin/env python3
import base64
import concurrent.futures
import cv2
import os
import pyaudio
import pynmea2
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
        self.data_gen

    def close(self):
        self._gps_uart.close()

    def _data_generator(self):
        '''Yield a tuple containing raw nmea data and parsed nmea data.'''
        while True:
            if self._gps_uart.inWaiting():
                recv = self._gps_uart.readline().decode()
                if '$GPGGA' in recv:
                    yield recv, pynmea2.parse(recv)
            else:
                time.sleep(0.01)


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
    frame = scipy.misc.imresize(frame, 25)
    enc_param = [int(cv2.IMWRITE_JPEG_QUALITY), 40]
    frame_enc = cv2.imencode('.jpeg', frame, enc_param)[1].tostring()
    frame_b64 = base64.encodebytes(frame_enc)
    socketIO.emit('frame', frame_b64.decode())


def frame_loop(sleep_time=1/100):
    cam = cv2.VideoCapture(0)
    while True:
        emit_frame(cam)
        time.sleep(sleep_time)


def emit_gps(recv, recv_parsed):
    socketIO.emit('gps', recv)
    socketIO.emit('coordinates', recv_parsed.latitude, recv_parsed.longitude)


def gps_loop():
    while True:
        recv, recv_parsed = next(gps.data_gen)
        log_data(recv_parsed)
        emit_gps(recv, recv_parsed)


def audio_callback(in_data, frame_count, time_info, status):
    # socketIO.emit('audio' in_data)
    return None, pyaudio.paContinue


if __name__ == '__main__':
    gps = ultimate_gps()
    socketIO = SocketIO(SERVER_IP, SERVER_PORT)
    pya = pyaudio.PyAudio()
    audio_stream = pya.open(format=pyaudio.paInt16,
                            channels=2,
                            rate=48000,
                            input=True,
                            frames_per_buffer=2048,
                            stream_callback=audio_callback)
    create_logfile()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(frame_loop)
        executor.submit(gps_loop)
