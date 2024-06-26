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

#define SOLENOID_VALVE 38

#define MUX1_S0 46
#define MUX1_S1 47
#define MUX1_S2 48
#define MUX1_S3 49
#define MUX1_SIG A0
#define MUX2_SIG A1
#define MUX_THRESHOLD 530 // From expermient

#define HALF_OF_SQUARES 16
#define SQUARES 32

#define LED1 22 // On/Off
#define LED2 23 // Start
#define LED3 24 // Set Home
#define LED4 25 // Ready
#define LED5 26 // Running
#define LED6 27 // Error
#define LED7 28 // Black Turn, win = blink
#define LED8 29 // White Turn, win = blink
#define LED9 30
#define LED10 31 // Draw

#define LIMIT_SWITCH1 34
#define LIMIT_SWITCH2 36
#define START_BUTTON 35
#define STOP_BUTTON 37
#define RESET_BUTTON 39
#define SETHOME_BUTTON 41

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

void initialize(){
  /*
  Set up the stepper motor drivers enable pins and solenoid valve's relay
  Stepper drivers are active high, we first set them to low to disable them
  The relay of solenoid valve is normally open, we set it to low to close the valve
  */
  pinMode(DRV1_EN, OUTPUT); digitalWrite(DRV1_EN, LOW);
  pinMode(DRV2_EN, OUTPUT); digitalWrite(DRV2_EN, LOW);
  pinMode(SOLENOID_VALVE, OUTPUT); digitalWrite(SOLENOID_VALVE, LOW);

  /*
  Set up the buttons and limit switches
  */
  pinMode(START_BUTTON, INPUT_PULLUP);
  pinMode(STOP_BUTTON, INPUT_PULLUP);
  pinMode(RESET_BUTTON, INPUT_PULLUP);
  pinMode(SETHOME_BUTTON, INPUT_PULLUP);
  pinMode(LIMIT_SWITCH1, INPUT_PULLUP);
  pinMode(LIMIT_SWITCH2, INPUT_PULLUP);

  /*
  Set up the LEDs
  */
  pinMode(LED1, OUTPUT); digitalWrite(LED1, LOW);
  pinMode(LED2, OUTPUT); digitalWrite(LED2, LOW);
  pinMode(LED3, OUTPUT); digitalWrite(LED3, LOW);
  pinMode(LED4, OUTPUT); digitalWrite(LED4, LOW);
  pinMode(LED5, OUTPUT); digitalWrite(LED5, LOW);
  pinMode(LED6, OUTPUT); digitalWrite(LED6, LOW);
  pinMode(LED7, OUTPUT); digitalWrite(LED7, LOW);
  pinMode(LED8, OUTPUT); digitalWrite(LED8, LOW);
  pinMode(LED9, OUTPUT); digitalWrite(LED9, LOW);
  pinMode(LED10, OUTPUT); digitalWrite(LED10, LOW);
}

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
  

  // Start interrupt
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