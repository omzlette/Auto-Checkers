#include <AccelStepper.h>
#include <MultiStepper.h>
#include <CD74HC4067.h>
// Define PINS
#define DRV1_EN 52
#define DRV2_EN 53

#define DRV1_DIR 2
#define DRV1_STEP 3
#define DRV2_DIR 4
#define DRV2_STEP 5

#define MUX_S0 6
#define MUX_S1 7
#define MUX_S2 8
#define MUX_S3 9
#define MUX1_SIG A0
#define MUX2_SIG A1
#define MUX_THRESHOLD 530 // From expermient

#define HALF_OF_SQUARES 16
#define SQUARES 32

#define SOLENOID_VALVE 10

// Declare Variables
AccelStepper stepper1(1, DRV1_STEP, DRV1_DIR);
AccelStepper stepper2(1, DRV2_STEP, DRV2_DIR);
MultiStepper steppers;

float desiredPos[2] = {0, 0};
bool toDesignatedPos = false;

CD74HC4067 mux1LogPINS(MUX_S0, MUX_S1, MUX_S2, MUX_S3);
CD74HC4067 mux2LogPINS(MUX_S0, MUX_S1, MUX_S2, MUX_S3);

int getBoardState();
void sendBoardState(int boardState);
int currentBoardState[8] = {0, 0, 0, 0, 0, 0, 0, 0};

void setup() {
  cli();

  // Set timer0 interrupt at 1MHz
  TCCR0A = 0; // set entire TCCR0A register to 0
  TCCR0B = 0; // same for TCCR0B
  TCNT0  = 0; // initialize counter value to 0
  // set compare match register for 1Mhz increments
  OCR0A = 15; // = (16*10^6) / (1*10^6) - 1 (must be <256)
  // turn on CTC mode
  TCCR0A |= (1 << WGM01);
  // Set CS01 and CS00 bits for 1 prescaler
  TCCR0B |= (1 << CS00);
  // enable timer compare interrupt
  TIMSK0 |= (1 << OCIE0A);

  // Set timer1 interrupt at 10kHz
  TCCR1A = 0; // set entire TCCR1A register to 0
  TCCR1B = 0; // same for TCCR1B
  TCNT1  = 0; // initialize counter value to 0
  // set compare match register for 1khz increments
  OCR1A = 1599; // = (16*10^6) / (1*10^4) - 1 (must be <65536)
  // turn on CTC mode
  TCCR1B |= (1 << WGM12);
  // Set CS12, CS11 and CS10 bits for 1 prescaler
  TCCR1B |= (1 << CS10)
  // enable timer compare interrupt
  TIMSK1 |= (1 << OCIE1A);

  // Set up the steppers
  

  sei();

}

ISR(TIMER0_COMPA_vect) {
  if(toDesignatedPos){
    steppers.moveTo(desiredPos);
  }
  steppers.run();
}

ISR(TIMER1_COMPA_vect) {
  // Get the current board state from the mux
}

void loop() {
  // put your main code here, to run repeatedly:
  switch (expression)
  {
  case 1:
    /* code */
    break;
  
  case 2:
    /* code */
    break;

  case 3:
    /* code */
    break;
  }
  
}

void setupStepper(){
  stepper1.setMaxSpeed(maxSPS);
  stepper2.setMaxSpeed(maxSPS);
  
  stepper1.setAcceleration(maxSPS*20);
  stepper2.setAcceleration(maxSPS*20);

  steppers.addStepper(stepper1);
  steppers.addStepper(stepper2);
}

int getBoardState(){
  int boardState_byte[8] = {0, 0, 0, 0, 0, 0, 0, 0};

  for(int idx = 0; idx < HALF_OF_SQUARES; idx++){
    mux1LogPINS.channel(idx);
    mux2LogPINS.channel(idx);
    int mux1Val = analogRead(MUX1_SIG);
    int mux2Val = analogRead(MUX2_SIG);
    if (mux1Val > MUX_THRESHOLD){
      if (floor(idx / 2) % 2 == 0){
        boardState_byte[idx] = 0 | (128 >> ((idx % 4) * 2) + 1);
      } else {
        boardState_byte[idx] = 0 | (128 >> ((idx % 4) * 2));
      }
    }
  }

  return boardState_byte;
}

void sendBoardState(int boardState){
  Serial.write(boardState);
}