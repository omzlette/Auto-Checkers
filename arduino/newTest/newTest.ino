#include <AccelStepper.h>

#define DRV1_EN 35

#define DRV1_DIR 4
#define DRV1_STEP 5

#define BUTTON_START 18

#define connectPin 22

const char DELIMITER = ';';

volatile unsigned long _millis = 0;
volatile unsigned long moveUpLast = 0;
volatile unsigned long moveDownLast = 0;
volatile unsigned long mainUpCntDown = 0;
volatile unsigned long mainDownCntDown = 0;
volatile unsigned long endCntDown = 0;

const float MICROSTEPS = 8;
const float maxSPS = 5026.19; // max angular vel * steps per rev / 2PI

const float movementGap = 888.51; // half a square == 25 mm -> (microstepsPerRev * half of square / pulleyRad * 2PI) usteps

unsigned long now = 0;
long currPos = 0;
float vel = 0;
long rawAngle = 0;
String inputString = "";
bool readingData = false;

volatile int speedDir = 0;
volatile bool Started = false;
volatile bool moveUp = false;
volatile bool moveDown = false;
volatile bool buttonPressed = false;
volatile bool forwardStarted = false;
volatile bool backwardStarted = false;
volatile bool ended = false;
volatile bool sendData = false;
volatile bool cooldown = false;
volatile bool run = false;

AccelStepper stepperX(1, DRV1_STEP, DRV1_DIR);

unsigned long Millis();

void setup(){
  cli();
  // 200kHz
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1  = 0;
  OCR1A = 79; // = (16*10^6) / prescaler / (200k) - 1
  TCCR1B |= (1 << WGM12);
  TCCR1B |= (1 << CS10); // prescaler = 1
  TIMSK1 |= (1 << OCIE1A);

  // 1kHz
  TCCR2A = 0;
  TCCR2B = 0;
  TCNT2  = 0;
  OCR2A = 124; // = (16*10^6) / prescaler / (1*10^3) - 1
  TCCR2A |= (1 << WGM21);
  TCCR2B |= (1 << CS22) | (1 << CS20); // prescaler = 128
  TIMSK2 |= (1 << OCIE2A);

  pinMode(BUTTON_START, INPUT_PULLUP);
  pinMode(DRV1_EN, OUTPUT); digitalWrite(DRV1_EN, LOW);
  pinMode(connectPin, OUTPUT); digitalWrite(connectPin, LOW);

  attachInterrupt(digitalPinToInterrupt(BUTTON_START), Start, FALLING);

  // stepperX.setPinsInverted(true, false, false);
  stepperX.setMaxSpeed(maxSPS);
  stepperX.setAcceleration(maxSPS * 100);
  
  Serial.begin(115200);

  sei();
}

ISR(TIMER1_COMPA_vect){
  if(buttonPressed){
    if(moveUp){
      stepperX.setSpeed(maxSPS);
      stepperX.runSpeed();
      if(_millis - moveUpLast > 80){
        Started = true;
        moveUp = false;
        stepperX.setCurrentPosition(0);
        forwardStarted = true;
        mainUpCntDown = _millis;
      }
    }

    if(Started){
      if(_millis - mainUpCntDown > 3000 && forwardStarted){
        stepperX.moveTo(movementGap * 15);
        stepperX.setSpeed(maxSPS);
        if(stepperX.distanceToGo() == 0){
          stepperX.setSpeed(0);
          forwardStarted = false;
          backwardStarted = true;
          mainDownCntDown = _millis;
        }
      }

      if(_millis - mainDownCntDown > 3000 && backwardStarted){
        stepperX.moveTo(0);
        stepperX.setSpeed(-maxSPS);
        if(stepperX.distanceToGo() == 0){
          stepperX.setSpeed(0);
          backwardStarted = false;
          Started = false;
          ended = true;
          endCntDown = _millis;
        }
      }
      stepperX.runSpeedToPosition();
      // stepperX.run();
    }

    if(_millis - endCntDown > 3000){
      if(ended){
        stepperX.setSpeed(0);
        ended = false;
        moveDown = true;
        moveDownLast = _millis;
      }
    }
    
    if(moveDown){
      stepperX.setSpeed(-maxSPS);
      stepperX.runSpeed();
      if(_millis - moveDownLast > 80){
        digitalWrite(DRV1_EN, LOW);
        digitalWrite(connectPin, LOW);
        moveDown = false;
        buttonPressed = false;
        cooldown = true;
      }
    }
  }
}

ISR(TIMER2_COMPA_vect) {
  _millis++;
  if(buttonPressed){
    sendData = true;
  }
}

unsigned long Millis(){
  return _millis;
}

void loop(){
  currPos = stepperX.currentPosition();
  vel = stepperX.speed();
  now = Millis();

  if(sendData){
    Serial.write((uint8_t*)&currPos, sizeof(currPos));
    Serial.write((uint8_t*)&vel, sizeof(vel));
    Serial.write((uint8_t*)&now, sizeof(now));
    sendData = false;
  }
}

void Start(){
  if(digitalRead(BUTTON_START) == 0){
    buttonPressed = true;
    moveUp = true;
    moveUpLast = Millis();
    digitalWrite(DRV1_EN, HIGH);
    digitalWrite(connectPin, HIGH);
  }
}