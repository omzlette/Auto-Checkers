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
volatile unsigned long startCntDown = 0;

const float MICROSTEPS = 8;
const float maxSPS = 5026.19; // max angular vel * steps per rev / 2PI

const float movementGap = 888.51; // half a square == 25 mm -> (microstepsPerRev * half of square / pulleyRad * 2PI) usteps

volatile unsigned long last = 0;
volatile unsigned long deltaDist = 0;
volatile long currPos = 0;
volatile float vel = 0;
volatile bool Started = false;
volatile bool moveUp = false;
volatile bool changeDir = false;
volatile bool buttonPressed = false;

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
  TIMSK2 |= (1 << OCIE2A) | (1 << OCIE2B);

  pinMode(18, INPUT_PULLUP);
  pinMode(19, OUTPUT); digitalWrite(19, LOW);
  pinMode(DRV1_EN, OUTPUT); digitalWrite(DRV1_EN, LOW);

  attachInterrupt(digitalPinToInterrupt(18), Start, FALLING);

  stepperX.setMaxSpeed(maxSPS);
  stepperX.setSpeed(maxSPS);
  stepperX.setAcceleration(maxSPS);

  Serial.begin(115200);

  sei();
}

ISR(TIMER1_COMPA_vect){
  // if(buttonPressed){
  //   if(!moveUp && !Started){
  //     stepperX.runSpeed();
  //     moveUp = true;
  //     moveUpLast = Millis();
  //   }
  //   else if(moveUp && !Started){
  //     stepperX.runSpeed();
  //     if(Millis() - moveUpLast >= 10){
  //       stepperX.stop();
  //       Started = true;
  //       startCntDown = Millis();
  //     }
  //   }

  //   if(Started){
  //     if(Millis() - startCntDown >= 1000){
  //       if(!changeDir){
  //         stepperX.moveTo(movementGap * 15);
  //         changeDir = true;
  //       }
  //       else if(changeDir && stepperX.distanceToGo() == 0){
  //         stepperX.moveTo(0);
  //       }
  //       stepperX.run();
  //     }
  //   }
  
  // }
}

ISR(TIMER2_COMPA_vect) {
  _millis++;
}

ISR(TIMER2_COMPB_vect) {
  // debug
  if(buttonPressed){
    static volatile unsigned long now = Millis();

    deltaDist = stepperX.distanceToGo();
    currPos = stepperX.currentPosition();
    vel = stepperX.speed();

        Serial.print(currPos);
        Serial.print(",");
        Serial.print(vel);
        Serial.print(",");
        Serial.print(now);

        Serial.print(",");
        Serial.println(Started);
  }
}

unsigned long Millis(){
  return _millis;
}

void loop(){
  
  // if(buttonPressed){
  //   if(!moveUp && !Started){
  //     stepperX.runSpeed();
  //     moveUp = true;
  //     moveUpLast = Millis();
  //   }
  //   else if(moveUp && !Started){
  //     stepperX.runSpeed();
  //     if(Millis() - moveUpLast >= 10){
  //       stepperX.stop();
  //       Started = true;
  //       startCntDown = Millis();
  //     }
  //   }

  //   if(Started){
  //     if(Millis() - startCntDown >= 1000){
  //       if(!changeDir){
  //         stepperX.moveTo(movementGap * 15);
  //         changeDir = true;
  //       }
  //       else if(changeDir && stepperX.distanceToGo() == 0){
  //         stepperX.moveTo(0);
  //       }
  //       stepperX.run();
  //     }
  //   }
  
  // }
  // stepperX.runSpeed();
}

void Start(){
  if(digitalRead(18) == 0){
    buttonPressed = true;
    digitalWrite(19, HIGH);

    digitalWrite(DRV1_EN, HIGH);
  }
}