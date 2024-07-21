#include <AccelStepper.h>
#include <Wire.h>
#include <AS5600.h>

#define DRV1_EN 35
#define DRV2_EN 37

#define DRV1_DIR 4
#define DRV1_STEP 5
#define DRV2_DIR 6
#define DRV2_STEP 7

#define BUTTON_START 18
#define BUTTON_FORWARD 19
#define BUTTON_BACKWARD 3
#define BUTTON_STOP 2

#define DEBUG_ERROR 22
#define DATA_FLAG 29
#define START_MATCH_FLAG 30

volatile unsigned long _millis = 0;
volatile unsigned long moveUpLast = 0;
volatile unsigned long moveDownLast = 0;
volatile unsigned long startCntDown = 0;
volatile unsigned long endCntDown = 0;

const float MICROSTEPS = 8;
const float maxSPS = 5026.19; // max angular vel * steps per rev / 2PI

const float movementGap = 888.51; // half a square == 25 mm -> (microstepsPerRev * half of square / pulleyRad * 2PI) usteps

volatile unsigned long now = 0;
volatile long currPos = 0;
volatile float vel = 0;
volatile long rawAngle = 0;
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

AccelStepper stepperX(1, DRV1_STEP, DRV1_DIR);
AccelStepper stepperY(1, DRV2_STEP, DRV2_DIR);
AMS_5600 encoder;

unsigned long Millis();

void setup(){
  cli();
  // Set timer1 interrupt at 10kHz
  TCCR1A = 0; // set entire TCCR1A register to 0
  TCCR1B = 0; // same for TCCR1B
  TCNT1  = 0; // initialize counter value to 0
  // set compare match register for 10khz increments
  OCR1A = 1599; // = (16*10^6) / (1*10^4) - 1 (must be <65536)
  // turn on CTC mode
  TCCR1B |= (1 << WGM12);
  // Set CS12, CS11 and CS10 bits for 1 prescaler
  TCCR1B |= (1 << CS10);
  // enable timer compare interrupt
  TIMSK1 |= (1 << OCIE1A);

  // Set timer2 interrupt at 1kHz
  TCCR2A = 0; // set entire TCCR0A register to 0
  TCCR2B = 0; // same for TCCR0B
  TCNT2  = 0; // initialize counter value to 0
  // set compare match register for 1khz increments
  OCR2A = 124; // = (16*10^6) / prescaler / (1*10^3) - 1 (must be <256)
  // turn on CTC mode
  TCCR2A |= (1 << WGM21);
  // Set 128 prescaler
  TCCR2B |= (1 << CS22) | (1 << CS20);
  // enable timer compare interrupt
  TIMSK2 |= (1 << OCIE2A);

  pinMode(BUTTON_START, INPUT_PULLUP);
  pinMode(BUTTON_FORWARD, INPUT_PULLUP);
  pinMode(BUTTON_BACKWARD, INPUT_PULLUP);
  pinMode(BUTTON_STOP, INPUT_PULLUP);
  pinMode(START_MATCH_FLAG, OUTPUT); digitalWrite(START_MATCH_FLAG, LOW);
  pinMode(DATA_FLAG, OUTPUT); digitalWrite(DATA_FLAG, LOW);
  pinMode(DRV1_EN, OUTPUT); digitalWrite(DRV1_EN, LOW);

  pinMode(DEBUG_ERROR, OUTPUT); digitalWrite(DEBUG_ERROR, LOW);

  attachInterrupt(digitalPinToInterrupt(BUTTON_START), Start, FALLING);
  attachInterrupt(digitalPinToInterrupt(BUTTON_FORWARD), Forward, FALLING);
  attachInterrupt(digitalPinToInterrupt(BUTTON_BACKWARD), Backward, FALLING);
  attachInterrupt(digitalPinToInterrupt(BUTTON_STOP), Stop, FALLING);

  stepperX.setPinsInverted(false, false, true);
  stepperX.setMaxSpeed(maxSPS);
  stepperX.setAcceleration(maxSPS * 100);

  Serial.begin(115220);
  Wire.begin();
  Wire.setClock(400000);

  sei();
}

ISR(TIMER1_COMPA_vect){
  if(moveUp && !Started){
    stepperX.setSpeed(maxSPS);
    stepperX.runSpeed();
    // run1 = true;
    if(Millis() - moveUpLast >= 220){
      Started = true;
      moveUp = false;
      startCntDown = Millis();
      stepperX.setCurrentPosition(0);
    }
  }

  if(Started){
    if(Millis() - startCntDown >= 500){
      digitalWrite(START_MATCH_FLAG, HIGH);
    }
    if(Millis() - startCntDown >= 1000){
      if(forwardStarted){
        stepperX.moveTo(movementGap * 15);
        speedDir = 1;
        forwardStarted = false;
      }
      else if(!forwardStarted && stepperX.distanceToGo() == 0){
        speedDir = 0;
        if(backwardStarted){
          stepperX.moveTo(0);
          speedDir = -1;
          backwardStarted = false;
          ended = true;
        }
      }
      
      if(ended && stepperX.distanceToGo() == 0){
        speedDir = 0;
        ended = false;
        cooldown = true;
        endCntDown = Millis();
      }
      stepperX.setSpeed(speedDir * maxSPS);
      stepperX.runSpeedToPosition();
      // run2 = true;

      if(cooldown && Millis() - endCntDown >= 500){
        digitalWrite(START_MATCH_FLAG, LOW);
        Started = false;
        cooldown = false;
      }
    }
  }

  if(moveDown){
    stepperX.setSpeed(-maxSPS);
    stepperX.runSpeed();
    // run1 = true;
    if(Millis() - moveDownLast >= 220){
      buttonPressed = false;
      moveDown = false;
      ended = false;
      digitalWrite(DRV1_EN, LOW);
      digitalWrite(DATA_FLAG, LOW);
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
  if(sendData){
    currPos = stepperX.currentPosition();
    vel = stepperX.speed();
    rawAngle = encoder.getRawAngle();
    now = Millis();
    Serial.write((uint8_t*)&currPos, sizeof(currPos));
    Serial.write((uint8_t*)&vel, sizeof(vel));
    Serial.write((uint8_t*)&rawAngle, sizeof(rawAngle));
    Serial.write((uint8_t*)&now, sizeof(now));
    sendData = false;
  }

  // if(run1){
  //   stepperX.runSpeed();
  //   run1 = false;
  // }

  // if(run2){
  //   stepperX.runSpeedToPosition();
  //   run2 = false;
  // }
}

void Start(){
  if(digitalRead(BUTTON_START) == 0){
    buttonPressed = true;
    moveUp = true;
    moveUpLast = Millis();
    digitalWrite(DATA_FLAG, HIGH);
    digitalWrite(DRV1_EN, HIGH);
  }
}

void Forward(){
  if(digitalRead(BUTTON_FORWARD) == 0){
    forwardStarted = true;
  }
}

void Backward(){
  if(digitalRead(BUTTON_BACKWARD) == 0){
    backwardStarted = true;
  }
}

void Stop(){
  if(digitalRead(BUTTON_STOP) == 0){
    moveDown = true;
    moveDownLast = Millis();
  }
}