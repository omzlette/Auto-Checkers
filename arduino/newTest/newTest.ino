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

#define HALF_OF_SQUARES 16
#define SQUARES 32

#define SOLENOID_VALVE 10

// Declare Variables
AccelStepper stepper2(1, DRV1_STEP, DRV1_DIR);
AccelStepper stepper1(1, DRV2_STEP, DRV2_DIR);
MultiStepper steppers;

float mux1Val[HALF_OF_SQUARES];  // Top half
float mux2Val[HALF_OF_SQUARES];  // Bottom half
float muxVal[SQUARES];
CD74HC4067 mux1LogPINS(MUX_S0, MUX_S1, MUX_S2, MUX_S3);
CD74HC4067 mux2LogPINS(MUX_S0, MUX_S1, MUX_S2, MUX_S3);

float StepsPerRev_Data = 200.0;               // From NEMA 17's Datasheet
float MICROSTEPS = 8;
float StepsPerRevolution = StepsPerRev_Data * MICROSTEPS; // usteps
float maxVel = 0.1 * sqrt(2);                 // m/s
float pulleyRadius = 0.007;                   // meters
float maxAngVel = maxVel / pulleyRadius;            // rad/s
float maxSPS = (maxAngVel * StepsPerRevolution) / (2 * PI); // usteps/s

float fullRevRAD = (2 * PI);
float fullRevMM = fullRevRAD * pulleyRadius;

unsigned long currentTime, previousTime;
bool done1 = false;
bool done2 = false;
bool done = false;
unsigned long freq = 1000; // kHz (1000 = mega)
unsigned long timeDelay = 1000 / freq; // us

// DEBUG
#define BUTTON 6

bool buttonState = LOW;                  // Current debounced button state
bool lastButtonState = LOW;              // Previous button state
bool startFlag = false;
bool Started = false;
long timerButton = 0;

bool DEBUG = true;
int count = 0;
unsigned long DEBUG_TIME, now, last;
bool DEBUG_RUNNING = true;

float moveHere = (StepsPerRevolution * 35 * sqrt(2)) / (14.33 * PI);           // full diagonal
long deltaDist_S1, currPos_S1;

float vel_S1, oldvel_S1, accel_S1;
long direction_S1;
unsigned long stepInterval;
long stepCounter;
float stepSize;

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

  // Set timer1 interrupt at 1kHz
  TCCR1A = 0; // set entire TCCR1A register to 0
  TCCR1B = 0; // same for TCCR1B
  TCNT1  = 0; // initialize counter value to 0
  // set compare match register for 1khz increments
  OCR1A = 15999; // = (16*10^6) / (1*10^3) - 1 (must be <65536)
  // turn on CTC mode
  TCCR1B |= (1 << WGM12);
  // Set CS12, CS11 and CS10 bits for 64 prescaler
  TCCR1B |= (1 << CS12) | (1 << CS10);
  // enable timer compare interrupt
  TIMSK1 |= (1 << OCIE1A);

  

  Serial.begin(115200);

  initPins();

  stepper1.setMaxSpeed(maxSPS);
  stepper2.setMaxSpeed(maxSPS);
  
  stepper1.setAcceleration(maxSPS*20);
  stepper2.setAcceleration(maxSPS*20);

  // steppers.addStepper(stepper1);
  // steppers.addStepper(stepper2);

  sei();
}

ISR(TIMER0_COMPA_vect) {
  if(Started){
    stepper1.moveTo(moveHere);
    stepper1.run();
    if(stepper1.distanceToGo() == 0){
      unsigned long delayTime = micros();
      while(micros() - delayTime < 1 * 1e+6){
        digitalWrite(31, HIGH);
      }
      if(moveHere == 0 && stepper1.distanceToGo() == 0){
        digitalWrite(DRV1_EN, LOW);
        digitalWrite(DRV2_EN, LOW);
        digitalWrite(31, LOW);
        startFlag = false;
        Started = false;
      }
      elif(moveHere != 0 && stepper1.distanceToGo() == 0){
        moveHere = 0;
      }
    }
  }
}

ISR(TIMER1_COMPA_vect) {
  if(DEBUG_RUNNING){
    debug();
  }
}

void loop() {
  // // getMUXValue();
  buttonState = !digitalRead(BUTTON);

  if(buttonState == HIGH && !startFlag){
    startFlag = true;
    timerButton = micros();
    // last = micros();
  }

  if(startFlag && !Started && micros() - timerButton >= 1 * 1e+6){
    Started = true;
    buttonState = LOW;
    digitalWrite(DRV1_EN, HIGH);
    digitalWrite(DRV2_EN, HIGH);
    digitalWrite(31, HIGH);
  }
  // // WORKING
  // // Add some conditions that will get a new "position" from path-finding
  // if(startFlag && Started){
  //   if(!done){
  //     DEBUG = true;
  //     long positions[2];

  //     positions[0] = moveHere;
  //     positions[1] = moveHere;

  //     stepper1.moveTo(moveHere);
  //     stepper2.moveTo(moveHere);

  //     digitalWrite(DRV1_EN, HIGH);
  //     digitalWrite(DRV2_EN, HIGH);
  //     digitalWrite(31, HIGH);

  //     previousTime = micros();
  //   }

  //   done1 = stepper1.distanceToGo() == 0;
  //   done2 = stepper2.distanceToGo() == 0;
  //   done = done1 && done2;
    
  //   if(done){
  //     // digitalWrite(DRV1_EN, LOW);
  //     // digitalWrite(DRV2_EN, LOW);
  //     digitalWrite(31, LOW);

  //     if(micros() - previousTime >= 2 * 1e+6){
  //       moveHere = 0;
  //       done = false;
  //       Started = false;
  //     }
  //   }
    
  //   stepper1.run(); // With acceleration, runToPosition() also use accel but don't use in loops
  //   // stepper1.runSpeedToPosition(); // Constant Speed
  //   stepper2.run();

  // }

}

void debug(){
  if(DEBUG){
    if(micros() - now >= timeDelay){
      now = micros();

      float deltaT = (now - last);

      deltaDist_S1 = stepper1.distanceToGo();
      currPos_S1 = stepper1.currentPosition();
      vel_S1 = stepper1.speed();

          Serial.print(currPos_S1);
          Serial.print(",");
          Serial.print(vel_S1);
          Serial.print(",");
          Serial.print(now);

          Serial.print(",");
          Serial.println(Started);

      last = micros();
    }
  }
}

void initPins(){
  pinMode(MUX1_SIG, INPUT);
  pinMode(MUX2_SIG, INPUT);

  pinMode(DRV1_EN, OUTPUT); digitalWrite(DRV1_EN, LOW);
  pinMode(DRV2_EN, OUTPUT); digitalWrite(DRV2_EN, LOW);

  pinMode(BUTTON, INPUT_PULLUP);
  pinMode(31, OUTPUT); digitalWrite(31, LOW);
  pinMode(33, OUTPUT); digitalWrite(33, LOW);
}

void getMUXValue() {
  float *muxPTR = muxVal;

  for(int idx = 0; idx < HALF_OF_SQUARES; idx++){
    mux1LogPINS.channel(idx);
    mux2LogPINS.channel(idx);
    mux1Val[idx] = analogRead(MUX1_SIG);
    mux2Val[idx] = analogRead(MUX2_SIG);
  }

  memcpy(muxVal, mux1Val, 16 * sizeof(float));
  memcpy(muxVal + HALF_OF_SQUARES, mux2Val, 16 * sizeof(float));
}

void sendToJetson(){
  // Send muxVal to Jetson
  for(int idx = 0; idx < SQUARES; idx++){
    Serial.print(muxVal[idx]);
    Serial.print(",");
  }
  Serial.println();
}

int velToSPS(int desireVel) {
  int desireAngVel, desireRPM, desireSPS;

  desireAngVel = desireVel / pulleyRadius;
  desireRPM = desireAngVel * 60 / 2 * PI;
  desireSPS = (desireRPM * StepsPerRevolution) / 60;

  return desireSPS;
}