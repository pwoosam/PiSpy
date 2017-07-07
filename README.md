# PiSpy
**GPS tracker with live audio and video**<br>
Get GPS coordinates as well as audio and video feed from your Raspberry Pi.

## Materials used
* Raspberry Pi 3
* Adafruit Ultimate GPS Breakout
* Raspberry Pi Camera Module V2
* Kinobo - USB 2.0 Mini Microphone
* Huawei E397u-53 4G LTE USB Modem
* Ting GSM SIM card

## Installation Instructions
**To setup Python 3 and it’s dependencies**
```
sudo apt install python3 python3-pip python3-numpy python3-scipy python3-serial cmake
sudo pip3 install -U pip wheel
sudo pip3 install pynmea2 socketIO-client
```

**For installing Huawei E397u-53 USB Modem using Ting SIM**<br>
Install networking and interface packages
```
sudo apt install modemmanager ppp usb-modeswitch wvdial
```
Setup ting network and usb_modeswitch
```
cd ~
mkdir cellular_setup
cd cellular_setup
wget http://www.kinisi.cc/s/Ting_wvdial.conf
sudo su
cat Ting_wvdial.conf > /etc/wvdial.conf
exit
```

Setup and install software to maintain connection to cellular data<br>
This keeps the modem alive and connected
```
wget "http://mintakaconciencia.net/squares/umtskeeper/src/umtskeeper.tar.gz"
mkdir ~/umtskeeper
tar -xzvf umtskeeper.tar.gz -C ~/umtskeeper
cd ~/umtskeeper
chmod +x sakis3g umtskeeper
wget “http://www.kinisi.cc/s/umtskeeper_rc.local”
# sudo cat umtskeeper_rc.local > /etc/rc.local  # but actually move contents above exit 0 in there
```
**For enabling the raspi camera**<br>
Add “sudo modprobe bcm2835-v4l2” to /etc/rc.local

**To install OpenCV**
```
sudo apt install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
sudo apt install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt install libxvidcore-dev libx264-dev
sudo apt install libgtk2.0-dev
sudo apt install libatlas-base-dev gfortran
cd ~
wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.2.0.zip
unzip opencv.zip
cd ~/opencv-3.2.0
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D PYTHON_INCLUDE_DIR=$(python3 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
    -D PYTHON_EXECUTABLE=$(which python3) \
    -D PYTHON_PACKAGES_PATH=$(python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") \
    -D BUILD_opencv_python2=OFF \
    -D BUILD_opencv_java=OFF \
    -D WITH_CUDA=OFF \
    -D BUILD_opencv_python3=ON \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_C_EXAMPLES=OFF \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D BUILD_EXAMPLES=OFF ..
make -j4
sudo make install
cd ~
```

**Free up some space**
```
sudo rm -R opencv-3.2.0
rm opencv.zip
```

**To enable the GPS**<br>
* for rpi3 or zero<br>
add sudo systemctl stop serial-getty@ttyS0.service to /etc/rc.local<br>
add sudo systemctl disable serial-getty@ttyS0.service to /etc/rc.local
* for rpi2 or 1<br>
add sudo systemctl stop serial-getty@ttyAMA0.service to /etc/rc.local<br>
add sudo systemctl disable serial-getty@ttyAMA0.service to /etc/rc.local
* for all<br>
remove console=serial0,115200 and/or anything similar from /boot/cmdline.txt
```
sudo chown pi:pi /dev/serial0
```

**To get the mic to work**
```
sudo apt install portaudio19-dev sox
sudo pip install pyaudio
```
