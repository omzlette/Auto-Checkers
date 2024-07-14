#include <AccelStepper.h>
#include <MultiStepper.h>

#define DRV1_EN 52
#define DRV2_EN 53

#define DRV1_DIR 2
#define DRV1_STEP 3
#define DRV2_DIR 4
#define DRV2_STEP 5

volatile unsigned long _millis = 0;
volatile unsigned long moveUpLast = 0;
volatile unsigned long moveDownLast = 0;
volatile unsigned long startCntDown = 0;
volatile unsigned long timeout = 0;

const float MICROSTEPS = 8;
const float maxSPS = 5026.19; // max angular vel * steps per rev / 2PI

const float movementGap = 888.51; // half a square == 25 mm -> (microstepsPerRev * half of square / pulleyRad * 2PI) usteps

volatile unsigned long last = 0;
volatile unsigned long now = 0;
volatile long currPos = 0;
volatile float vel = 0;
volatile bool Started = false;
volatile bool moveUp = false;
volatile bool moveDown = false;
volatile bool changeDir = false;
volatile bool buttonPressed = false;
volatile bool ended = false;
volatile bool sendData = false;
volatile bool timeoutFlag = false;

AccelStepper stepperX(1, DRV1_STEP, DRV1_DIR);
AccelStepper stepperY(1, DRV2_STEP, DRV2_DIR);
MultiStepper steppers;

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
  TIMSK2 |= (1 << OCIE2B) | (1 << OCIE2A);

  pinMode(4, OUTPUT); digitalWrite(4, LOW);
  pinMode(18, INPUT_PULLUP);
  pinMode(19, OUTPUT); digitalWrite(19, LOW);
  pinMode(20, OUTPUT); digitalWrite(20, LOW);
  pinMode(DRV1_EN, OUTPUT); digitalWrite(DRV1_EN, LOW);

  attachInterrupt(digitalPinToInterrupt(18), Start, FALLING);

  stepperX.setPinsInverted(false, false, true);
  stepperX.setMaxSpeed(maxSPS);
  stepperX.setAcceleration(maxSPS * 100);

  Serial.begin(115200);

  sei();
}

ISR(TIMER1_COMPA_vect){
  if(buttonPressed){
    timeout = false;
    if(!moveUp && !Started){
      moveUp = true;
      moveUpLast = Millis();
    }
    else if(moveUp && !Started){
      stepperX.setSpeed(maxSPS);
      stepperX.runSpeed();
      if(Millis() - moveUpLast >= 200){
        Started = true;
        startCntDown = Millis();
        stepperX.setCurrentPosition(0);
      }
    }

    if(Started){
      digitalWrite(19, HIGH);
      if(Millis() - startCntDown >= 1000){
        if(!changeDir){
          stepperX.moveTo(movementGap * 15);
          stepperX.setSpeed(maxSPS);
          changeDir = true;
        }
        else if(changeDir && stepperX.distanceToGo() == 0){
          stepperX.moveTo(0);
          stepperX.setSpeed(maxSPS);
          startCntDown = Millis();
          ended = true;
        }
        stepperX.runSpeedToPosition();
        // stepperX.run();
        if(ended && stepperX.distanceToGo() == 0){
          moveUp = false;
          Started = false;
          changeDir = false;
          buttonPressed = false;
          timeoutFlag = true;
          timeout = Millis();

          digitalWrite(4, LOW);
          digitalWrite(19, LOW);
        }
      }
    }
  }
  if(timeoutFlag){
    if(Millis() - timeout >= 1000){
      moveDown = true;
      moveDownLast = Millis();
      timeoutFlag = false;
    }
  }

  if(moveDown){
    stepperX.setSpeed(-maxSPS);
    stepperX.runSpeed();
    if(Millis() - moveDownLast >= 100){
      moveDown = false;
      timeoutFlag = false;
      digitalWrite(DRV1_EN, LOW);
      digitalWrite(20, LOW);
    }
  }
  currPos = stepperX.currentPosition();
  vel = stepperX.speed();
  now = Millis();
}

ISR(TIMER2_COMPA_vect) {
  _millis++;
}

ISR(TIMER2_COMPB_vect) {
  if(buttonPressed){
    sendData = true;
  }
}

unsigned long Millis(){
  return _millis;
}

void loop(){
  if(sendData){
    Serial.write((uint8_t*)&currPos, sizeof(currPos));
    Serial.write((uint8_t*)&vel, sizeof(vel));
    Serial.write((uint8_t*)&now, sizeof(now));
    Serial.write(Started);
    sendData = false;
    last = Millis();
  }
}

void Start(){
  if(digitalRead(18) == 0){
    buttonPressed = true;
    digitalWrite(20, HIGH);
    digitalWrite(DRV1_EN, HIGH);
  }
}