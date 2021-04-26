# Self Driving Car Project
![alt text](https://github.com/AdityaNG/Self-Driving-RC-Car/blob/master/images/predict.gif "Predicitons")
![alt text](https://github.com/AdityaNG/Self-Driving-RC-Car/blob/master/images/webInterface.png "Web Interface")
## Description
To build the software infrastructure needed for:
1. Controlling a car - Being able to remotely pilot a car via the web interface or a bluetooth controller
2. Recording training data - Being able to record multiple video streams and sensors along with CAN data like wheel speed, steering angle, throttle, brake
3. Replaying the training data - Having a quick and easy interface to replay the training data with all the video feeds and sensor data at a quick glance

![alt text](https://github.com/AdityaNG/Self-Driving-RC-Car/blob/master/images/car.jpg "The Car")

## Progress so far
### Controlling the Car
Right now, there are three options to control the car wirelessly
1. Web interface - Works universally
2. Bluetooth Controller - Hardcodded button values as of now
3. Command Line Interface - Works universally

### Recording training data
Training Data can be recorded and downloaded via the web interface. The data gets recorded to the 'web/training_data/' folder and is compressed into a zip file so it can be easily downloaded.

![alt text](https://github.com/AdityaNG/Self-Driving-RC-Car/blob/master/images/cannyEdges.png "Canny Edge Detection")
![alt text](https://github.com/AdityaNG/Self-Driving-RC-Car/blob/master/images/laneMarkings.png "Lane Markings")

Right now, it only records camera data for the primary Raspberry Pi camera along with throttle, steering and brake values
The format of storage of this data is :

* data_folder/
    - data.csv
    - player.py
    - images/
        - 1589202544.57268.jpg
		- 1589202545.33127.jpg
        ...
        - 1589203451.23581.jpg

### Installation
This project requires a few python dependencies to run.
Install the dependencies with
```sh
$ git clone https://github.com/AdityaNG/Self-Driving-RC-Car.git
$ cd Self-Driving-RC-Car.git/web
$ ./install.sh
```

#### Getting Started
![alt text](https://github.com/AdityaNG/Self-Driving-RC-Car/blob/master/images/wiring.jpg "Wiring")
Wire up the Raspberry Pi to your motor controller as 
* Forawrd / Backward Pins
    - in1 = 27
    - in2 = 17
    - en = 22
* Left / Right Pins
    - tin1 = 23
    - tin2 = 24
    - ten = 25

Clone this repo and start up the web interface
```sh
$ ./start.sh
```
The web interface should be available at http://device.ip:8080/
To stop the web interface, type
```sh
$ ./stop.sh
```
### Development
Want to contribute? Great!
We can get in touch at adityang5@gmail.com
### Todos

 - Bluetooth
    - Add better bluetooth controller support
    - Remappable bluetooth controller
    - Add record, brake, features to bluetooth
    - Auto boot to bluetooth
    - Web interface to setup bluetooth controller
 - Add temperature monitoring support for motor, MCU, BMS, etc.
 - Add CAN Bus monitoring support
 - Measure dropped frames
 - Add support for general Linux systems

License
----

MIT


**Free Software, Hell Yeah!**

