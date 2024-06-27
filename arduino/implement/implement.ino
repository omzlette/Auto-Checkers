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

#define MUX_S0 46
#define MUX_S1 47
#define MUX_S2 48
#define MUX_S3 49
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

#define MAX_BUFFER_LENGTH 32

// Declare Variables
AccelStepper stepper1(1, DRV1_STEP, DRV1_DIR);
AccelStepper stepper2(1, DRV2_STEP, DRV2_DIR);
MultiStepper steppers;

CD74HC4067 mux1LogPINS(MUX_S0, MUX_S1, MUX_S2, MUX_S3);
CD74HC4067 mux2LogPINS(MUX_S0, MUX_S1, MUX_S2, MUX_S3);

/*
Pulley Radius : 7.165mm
1 Microsteps : 1/8 step
Steps per revolution (Datasheet) : 200
Max Linear Velocity : 0.1 sqrt2 m/s
Max Angular Velocity : 19.7378 rad/s
*/

const float MICROSTEPS = 8;
const float maxSPS = 5026.19; // max angular vel * steps per rev / 2PI

const float movementGap = 888.51; // half a square == 25 mm -> (microstepsPerRev * half of square / pulleyRad * 2PI) usteps

float desiredPos[2] = {0, 0};
bool toDesignatedPos = false;

enum {CONNECTED, DISCONNECTED} connection = DISCONNECTED;
enum {INIT, IDLE, RUNNING, ERROR} state = INIT;

const char DELIMITER = ';';
const uint8_t ACK = 0x50;
const uint8_t CMPLT = 0x51;
const uint8_t NACK = 0x60;

// Declare Functions

void initialize();
void setupStepper();

void sendBoardData();

void stateManagement(const byte mode, const char * data);
void processIncomingByte(const byte inByte);

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

  // Initialize everything
  initialize();
  setupStepper();

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
  // might not be needed
}

void loop() {
  while(Serial.available() > 0){
    processIncomingByte(Serial.read());
  }
}

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
  Set up the multiplexer signal pins
  */
  pinMode(MUX1_SIG, INPUT);
  pinMode(MUX2_SIG, INPUT);

  /*
  Set up the buttons and limit switches
  */
  pinMode(START_BUTTON, INPUT);
  pinMode(STOP_BUTTON, INPUT);
  pinMode(RESET_BUTTON, INPUT);
  pinMode(SETHOME_BUTTON, INPUT);
  pinMode(LIMIT_SWITCH1, INPUT);
  pinMode(LIMIT_SWITCH2, INPUT);

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

void setupStepper(){
  stepper1.setMaxSpeed(maxSPS);
  stepper2.setMaxSpeed(maxSPS);
  
  stepper1.setAcceleration(maxSPS*20);
  stepper2.setAcceleration(maxSPS*20);

  steppers.addStepper(stepper1);
  steppers.addStepper(stepper2);
}

void sendBoardData(){
  /*
  Hall Sensor location
  x 0 x 1 x 2 x 3
  4 x 5 x 6 x 7 x
  x 8 x 9 x A x B
  C x D x E x F x
  x 0 x 1 x 2 x 3
  4 x 5 x 6 x 7 x
  x 8 x 9 x A x B
  C x D x E x F x

  */
  uint8_t boardState_row1 = 0;
  uint8_t boardState_row2 = 0;
  uint8_t boardState_buffer[8] = {0, 0, 0, 0, 0, 0, 0, 0};

  for(int idx = 0; idx < HALF_OF_SQUARES; idx++){
    mux1LogPINS.channel(idx);
    mux2LogPINS.channel(idx);
    int mux1Val = analogRead(MUX1_SIG);
    int mux2Val = analogRead(MUX2_SIG);
    if (mux1Val > MUX_THRESHOLD){
      switch(floor(idx / 4) % 2){
        case 0:
          boardState_row1 |= ((idx % 4) * 2) + 1;
          break;
        case 1:
          boardState_row1 |= ((idx % 4) * 2);
          break;
      }
    }
    if (mux2Val > MUX_THRESHOLD){
      switch(floor(idx / 4) % 2){
        case 0:
          boardState_row2 |= ((idx % 4) * 2) + 1;
          break;
        case 1:
          boardState_row2 |= ((idx % 4) * 2);
          break;
      }
    }

    if (idx % 4 == 3){
      boardState_buffer[floor(idx / 4)] = boardState_row1;
      boardState_buffer[floor(idx / 4) + 4] = boardState_row2;
      boardState_row1 = 0;
      boardState_row2 = 0;
    }
  }

  Serial.write(boardState_buffer, 8);
  Serial.write(DELIMITER);
}

void stateManagement(const byte mode, const char * data){
  /*
  Process the data received from the Jetson
  */
  switch (connection){
    case DISCONNECTED:
      switch (mode){
        case 0xF0:  // Connection request
          connection = CONNECTED;
          Serial.write(ACK);
          break;
        default:
          Serial.write(NACK);
          break;
      }
      break;
    
    case CONNECTED:
      switch (mode){
        // Mode 0xF1: Requested for board state
        case 0xF1:
          sendBoardData();
          // then wait for ack
          break;
        // Mode 0xF2: Requested for stepper movement
        case 0xF2:
          break;
        // Mode 0xF3: Requested for status indication
        case 0xF3:
          break;
        // Mode 0xFF: Disconnection request
        case 0xFF:
          connection = DISCONNECTED;
          Serial.write(ACK);
          break;
        // invalid mode (unknown command, should not happen)
        default:
          Serial.write(NACK);
          break;
      }
      break;
  }
  
}

void processIncomingByte(const byte inByte){
  /*
  Process the incoming byte from the Jetson
  */
  static char RxBuffer [MAX_BUFFER_LENGTH];
  static char dataBuffer [MAX_BUFFER_LENGTH];
  static unsigned int bufferIDX = 0;
  static byte mode = 0;
  static bool mode_received = false;
  static byte checksum = 0;

  switch (inByte)
  {
  case DELIMITER:   // end of text
    RxBuffer[bufferIDX] = 0;  // terminating null byte

    if (mode_received){
      byte calculatedChecksum = mode;
      for (int i = 0; i < bufferIDX - 1; i++){
        calculatedChecksum ^= RxBuffer[i];
        dataBuffer[i] = RxBuffer[i];
      }

      if (calculatedChecksum == checksum){
        // Checksum is correct, send ACK and process the data
        Serial.write(ACK);
        stateManagement(mode, dataBuffer);
      }
      else{
        // Checksum is incorrect, send NACK
        Serial.write(NACK);
      }
    }

    // reset buffer for next time
    bufferIDX = 0;
    break;

  case '\r':   // discard carriage return
    break;

  case '\n':   // discard line feed
    break;

  default:
    // keep adding if not full ... allow for terminating null byte
    if (!mode_received){
      mode = inByte;
      mode_received = true;
      checksum = inByte;
    }
    else{
      if (bufferIDX < (MAX_BUFFER_LENGTH - 1)){
        RxBuffer[bufferIDX] = inByte;
        checksum = inByte;
        bufferIDX++;
      }
    }
    break;
  }
}