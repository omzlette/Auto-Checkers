#include <AccelStepper.h>
#include <MultiStepper.h>
#include <AS5600.h>
#include <Wire.h>

#define DRV1_EN 35

#define DRV1_DIR 4
#define DRV1_STEP 5

#define BUTTON 2

const float maxSPS = 5026.19;
const float movementGap = 888.51;
const int moveIDX[4] = {14, 12, 12, 10};

volatile unsigned long blinkTimer = 0;
volatile unsigned long blinkTimer2 = 0;

volatile bool moveCount = 0;
volatile int prevMove = 0;
volatile int moveDIR = 1;

AccelStepper stepperX(1, DRV1_STEP, DRV1_DIR);
AMS_5600 encoder;

void setup() {
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

  pinMode(DRV1_EN, OUTPUT); digitalWrite(DRV1_EN, LOW);
  pinMode(BUTTON, INPUT_PULLUP);
  pinMode(22, OUTPUT); digitalWrite(22, LOW);
  pinMode(23, OUTPUT); digitalWrite(23, LOW);
  pinMode(41, OUTPUT); digitalWrite(41, LOW);

  attachInterrupt(digitalPinToInterrupt(BUTTON), [](){
    if(digitalRead(BUTTON) == LOW){
      digitalWrite(23, !digitalRead(23));
    }
  }, FALLING);

  // pinMode(DRV1_EN, OUTPUT); digitalWrite(DRV1_EN, HIGH);

  stepperX.setMaxSpeed(maxSPS);
  stepperX.setAcceleration(maxSPS * 20);

  // Wire.begin();
  // Wire.setClock(400000);

  // encoder.begin(41);


  Serial.begin(115200);
  sei();
}

ISR(TIMER1_COMPA_vect){
  // if(stepperX.distanceToGo() == 0){
  //   moveCount++;
  // }
  // moveDIR = prevMove < moveIDX[moveCount] ? 1 : -1;
  // prevMove = moveIDX[moveCount];
  // stepperX.moveTo(movementGap * 2);
  // stepperX.setSpeed(maxSPS);
  // stepperX.runSpeed();
}

ISR(TIMER2_COMPA_vect){
  blinkTimer++;
  if(blinkTimer % 1000 == 0){
    digitalWrite(22, !digitalRead(22));
  }
}

ISR(TIMER2_COMPB_vect){
//   blinkTimer2++;
//   if(blinkTimer2 % 100 == 0){
//     digitalWrite(23, !digitalRead(23));
//     // Serial.println(blinkTimer);
//   }
}

void loop() {
  // put your main code here, to run repeatedly:

}
