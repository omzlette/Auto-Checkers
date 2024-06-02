#include <Wire.h>
#include <AS5600.h>
#include <eRCaGuy_Timer2_Counter.h>

#define DIR_PIN 2
#define BUTTON 4

AMS_5600 encoder;

bool startFlag = false;

float currentAngle = 0;
float previousAngle = 0;
float continuousAngle = 0.0;
float prevContAngle = 0.0;
int numRevolutions = 0;
float timeLast = 0;
float timeNow = 0;
float pulleyRadius = 0.007; // meters

unsigned long now = 0;
unsigned long freq = 1000; // kHz (1000 = mega)
unsigned long timeDelay = 1000 / freq; // us

float rawAngleArray[20000];
float angleArray[20000];
float timeArray[20000];
bool flagArray[20000];

int debugIDX = 0;

float mapfloat(long x, long in_min, long in_max, long out_min, long out_max)
{
  return (float)(x - in_min) * (out_max - out_min) / (float)(in_max - in_min) + out_min;
}

float Angle(){
  float in;
  in = mapfloat(encoder.getRawAngle(), 0, 4095, 0, 360);
  // Serial.print(encoder.getRawAngle());
  // Serial.print(",");
  return in;
}

void output(float angle){
  bool Started = digitalRead(8);
  timeNow = timer2.get_count()/2;

  Serial.print(angle);
  Serial.print(",");
  Serial.print(timeNow);
  Serial.print(",");
  Serial.println(Started);
}

void setup() {
  timer2.setup();

  pinMode(DIR_PIN, OUTPUT);
  pinMode(BUTTON, INPUT_PULLUP);
  pinMode(8, INPUT);
  Serial.begin(1000000);
  Wire.begin();
  Wire.setClock(400000);

  Serial.println("---------");
  Serial.println("Raw Input, Angle, Time, Started");
  digitalWrite(DIR_PIN, HIGH);
}

void loop() {
  int buttonState = !digitalRead(BUTTON);
  if(buttonState == 1 && startFlag == false){
    startFlag = true;
    timeLast = timer2.get_count()/2;
  }

  if(startFlag){
    if((timer2.get_count() - now)/2 >= timeDelay){
      now = timer2.get_count();
      currentAngle = Angle();
      if(currentAngle - previousAngle > 180){
        numRevolutions--;
      } else if(currentAngle - previousAngle < -180){
        numRevolutions++;
      }
      continuousAngle = currentAngle + (numRevolutions * 360);

      previousAngle = currentAngle;
      output(continuousAngle);
    }
  }
}