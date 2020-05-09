/* Sweep
 by BARRAGAN <http://barraganstudio.com>
 This example code is in the public domain.

 modified 8 Nov 2013
 by Scott Fitzgerald
 http://www.arduino.cc/en/Tutorial/Sweep
*/

#include <Servo.h>
const int pingPin = 7; // Trigger Pin of Ultrasonic Sensor
const int echoPin = 6; // Echo Pin of Ultrasonic Sensor

Servo myservo, myservo1;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int theta = 0, phi = 60, f1=1, f=1, m1=20, m=20;    // variable to store the servo phiition
//int lb=100,ub=160, lb1=60, ub1=160;

int lb1=70,ub1=180, lb=100, ub=120;

int incomingByte = 0; // for incoming serial data

//int lb=100,ub=160, lb1=109, ub1=111;

void setup() {
  myservo1.attach(10);  // attaches the servo on pin 9 to the servo object
  myservo.attach(9);
  Serial.begin(115200); // Starting Serial Terminal
  phi = lb, theta = lb1;
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB
  }
}


void loop() {
  //myservo.write(180);
  //myservo1.write(120);
  //return;
  
  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.read();

    // say what you got:
    Serial.print("I received: ");
    Serial.println(incomingByte, DEC);
    if (true) {
        
  long duration, inches, r;
   pinMode(pingPin, OUTPUT);
   digitalWrite(pingPin, LOW);
   delayMicroseconds(2);
   digitalWrite(pingPin, HIGH);
   delayMicroseconds(10);
   digitalWrite(pingPin, LOW);
   pinMode(echoPin, INPUT);
   duration = pulseIn(echoPin, HIGH);
   inches = microsecondsToInches(duration);
   r = microsecondsToCentimeters(duration);
   //Serial.print(inches);
   //Serial.print("in, ");
   if (r<50) {
     Serial.print(r);
     Serial.print(" ");
     Serial.print(theta);
     Serial.print(" ");
     Serial.print(phi);
     Serial.print(" ");
     Serial.println();
   }
  theta += f1*m1;
  if (!(lb1<=theta && theta<=ub1)) {
    if (theta>=ub1) {
      f1 = -1;
    } else if (theta<=lb1) {
      f1 = 1;
    } else {
      theta = lb1;
      f1 = 1;
    }

    phi += f*m;
    if (!(lb<=phi && phi<=ub)) {
      if (phi>=ub) {
        f = -1;
      } else if (phi<=lb) {
        f = 1;
      } else {
        phi = lb;
        f = 1;
      }
    }
  }
  myservo.write(phi);
  myservo1.write(theta);
delay(100);
    }
  }
}

long microsecondsToInches(long microseconds) {
   return microseconds / 74 / 2;
}

long microsecondsToCentimeters(long microseconds) {
   return microseconds / 29 / 2;
}
