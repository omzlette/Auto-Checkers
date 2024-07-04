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

#define LED1_ONOFF 22 // On/Off
#define LED2_START 23 // Start
#define LED3_SETHOME 24 // Set Home
#define LED4_READY 25 // Ready
#define LED5_RUNNING 26 // Running
#define LED6_ERROR 27 // Error
#define LED7_BTURN 28 // Black Turn, win = blink
#define LED8_WTURN 29 // White Turn, win = blink
#define LED9 30
#define LED10_DRAW 31 // Draw

#define LIMIT_SWITCH1 34
#define LIMIT_SWITCH2 36
#define START_BUTTON 18
#define STOP_BUTTON 19
#define RESET_BUTTON 20
#define SETHOME_BUTTON 21

#define MAX_BUFFER_LENGTH 32

// Declare Variables
AccelStepper stepperX(1, DRV1_STEP, DRV1_DIR);
AccelStepper stepperY(1, DRV2_STEP, DRV2_DIR);
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

volatile unsigned long _millis = 0;
volatile unsigned long _LEDBlink = 0;
// volatile unsigned long _timerDebug_Millis = 0;

const float MICROSTEPS = 8;
const float maxSPS = 5026.19; // max angular vel * steps per rev / 2PI

const float movementGap = 888.51; // half a square == 25 mm -> (microstepsPerRev * half of square / pulleyRad * 2PI) usteps

volatile long desiredPos[2] = {0, 0};
volatile int posIDX = 0;
volatile bool toDesignatedPos = false;
volatile bool reachedDesignatedPos = false;
volatile bool triggerSolenoid = false;

bool allRunningDone = false;
bool drawStatus = false;
bool whiteWinStatus = false;
bool blackWinStatus = false;
bool blackTurnStatus = false;
bool whiteTurnStatus = false;
bool errorStatus = false;
bool illegalMoveStatus = false;

volatile bool startButton = false;
volatile bool stopButton = false;
volatile bool resetButton = false;
volatile bool setHomeButton = false;
volatile bool limitSwitch1 = false;
volatile bool limitSwitch2 = false;

bool sentStartStatus = false;
bool sentStopStatus = false;
bool sentResetStatus = false;
bool receivedACK = false;
volatile byte _mode = 0;
volatile const char * _dataBuffer = NULL;
volatile unsigned int _dataLength = 0;

enum {CONNECTED, DISCONNECTED} connection = DISCONNECTED;
enum {SETHOME_IDLE, START_IDLE, STOP_IDLE, RESET_IDLE, IDLE, MOTOR_RUNNING, ERROR} state = SETHOME_IDLE;

const char DELIMITER = ';';
const uint8_t ACK = 0x50;
const uint8_t CMPLT = 0x51;
const uint8_t NACK = 0x60;

// Functions
unsigned long Millis();

void initialize();
void setupStepper();

void sendBoardData();
void movementMapping(const char x, const char y);
void updateStatus(const char status);

void stateManagement(const byte mode, const char * data, const unsigned int dataLength);
void processIncomingByte(const byte inByte);
bool isACK(const byte inByte);

void setup() {
  cli();

  // Set timer1 interrupt at 10kHz
  TCCR1A = 0; // set entire TCCR1A register to 0
  TCCR1B = 0; // same for TCCR1B
  TCNT1  = 0; // initialize counter value to 0
  // set compare match register for 1khz increments
  OCR1A = 1599; // = (16*10^6) / (1*10^4) - 1 (must be <65536)
  // turn on CTC mode
  TCCR1B |= (1 << WGM12);
  // Set CS12, CS11 and CS10 bits for 1 prescaler
  TCCR1B |= (1 << CS10);
  // enable timer compare interrupt
  TIMSK1 |= (1 << OCIE1A);

  // Set timer2 interrupt at 10kHz
  TCCR2A = 0; // set entire TCCR0A register to 0
  TCCR2B = 0; // same for TCCR0B
  TCNT2  = 0; // initialize counter value to 0
  // set compare match register for 10khz increments
  OCR2A = 124; // = (16*10^6) / prescaler / (1*10^3) - 1 (must be <256)
  // turn on CTC mode
  TCCR2A |= (1 << WGM21);
  // Set 128 prescaler
  TCCR2B |= (1 << CS22) | (1 << CS20);
  // enable timer compare interrupt
  TIMSK2 |= (1 << OCIE2A) | (1 << OCIE2B);

  // Initialize everything
  initialize();
  setupStepper();

  // Set up serial communication
  Serial.begin(115200);

  // Set up buttons
  attachInterrupt(digitalPinToInterrupt(START_BUTTON), []{if(digitalRead(START_BUTTON) == 0){startButton = true;}}, FALLING);
  attachInterrupt(digitalPinToInterrupt(STOP_BUTTON), []{if(digitalRead(STOP_BUTTON) == 0){stopButton = true;}}, FALLING);
  attachInterrupt(digitalPinToInterrupt(RESET_BUTTON), []{if(digitalRead(RESET_BUTTON) == 0){resetButton = true;}}, FALLING);
  attachInterrupt(digitalPinToInterrupt(SETHOME_BUTTON), []{if(digitalRead(SETHOME_BUTTON) == 0){setHomeButton = true;}}, FALLING);

  // Start interrupts
  sei();

}

ISR(TIMER1_COMPA_vect) {
  /*
  run() function calls runSpeed() function at least every step interval
  as stated in the description of the runSpeed() function.

  As we are using 8 microsteps per step, we need to call runSpeed()
  
  */
  if(connection == CONNECTED){
    switch(state){
      case SETHOME_IDLE:
        digitalWrite(LED4_READY, LOW);
        if(setHomeButton){
          digitalWrite(LED3_SETHOME, HIGH);
          digitalWrite(LED5_RUNNING, HIGH);

          digitalWrite(DRV1_EN, HIGH);
          digitalWrite(DRV2_EN, HIGH);

          stepperX.setSpeed(-maxSPS);
          stepperY.setSpeed(-maxSPS);
          stepperX.runSpeed();
          stepperY.runSpeed();
        }
        // to START_IDLE
        if(limitSwitch1 && limitSwitch2){
          stepperX.setCurrentPosition(0);
          stepperY.setCurrentPosition(0);
          digitalWrite(DRV1_EN, LOW);
          digitalWrite(DRV2_EN, LOW);
          digitlaWrite(LED3_SETHOME, LOW);
          digitalWrite(LED5_RUNNING, LOW);
          setHomeButton = false;
          state = START_IDLE;
        }
        break;

      case START_IDLE:
        digitalWrite(LED4_READY, LOW);
        if(startButton && !sentStartStatus){
          digitalWrite(LED2_START, HIGH);

          Serial.write(0x99);
          Serial.write(';');
          sentStartStatus = true;
          startButton = false;
        }
        
        if(sentStartStatus && receivedACK){
          // receive ACK => change state to IDLE
          state = IDLE;
          sentStartStatus = false;
          receivedACK = false;
        }

        break;

      case RESET_IDLE:
        if(resetButton && !sentResetStatus){
          digitalWrite(LED4_READY, LOW);

          Serial.write(0x97);
          Serial.write(';');
          sentResetStatus = true;
          resetButton = false;
        }

        if(sentResetStatus && receivedACK){
          // receive ACK => change state to SETHOME_IDLE
          state = SETHOME_IDLE;
          sentResetStatus = false;
          receivedACK = false;
        }

        break;

      case IDLE:
        if(blackWinStatus | whiteWinStatus){
          state = RESET_IDLE;
        }

        if(stopButton && !sentStopStatus){
          digitalWrite(LED5_RUNNING, LOW);
          digitalWrite(DRV1_EN, LOW);
          digitalWrite(DRV2_EN, LOW);

          Serial.write(0x98);
          Serial.write(';');
          sentStopStatus = true;
          stopButton = false;
        }

        if(sentStopStatus && receivedACK){
          // receive ACK => change state to SETHOME_IDLE
          state = SETHOME_IDLE;
          sentStopStatus = false;
          receivedACK = false;
        }

        switch(_mode){
          case 0xF1:
            //wait for ACK
            if(receivedACK){
              state = IDLE;
              _mode = 0;
              receivedACK = false;
            }
            break;
        }
        break;

      case MOTOR_RUNNING:
        if(!reachedDesignatedPos){
          digitalWrite(LED5_RUNNING, HIGH);

          digitalWrite(DRV1_EN, HIGH);
          digitalWrite(DRV2_EN, HIGH);

          // do posiition management (array loop w/o loop)
          if(!allRunningDone){
            if(!toDesignatedPos){
              if(posIDX < _dataLength){
                  // get the desired position (x, y
                char x = _dataBuffer[posIDX];
                char y = _dataBuffer[posIDX + 1];
                movementMapping(x, y);
                posIDX += 2;
                reachedDesignatedPos = false;
              }
              else{
                allRunningDone = true;
              }
            }
          }
          else{
            digitalWrite(DRV1_EN, LOW);
            digitalWrite(DRV2_EN, LOW);
            digitalWrite(LED5_RUNNING, LOW);
            digitalWrite(LED2_START, LOW);

            digitalWrite(SOLENOID_VALVE, LOW);
            triggerSolenoid = false;

            Serial.write(CMPLT);
            state = IDLE;
          }

          // set the desired position one by one
          stepperX.moveTo(desiredPos[0]);
          stepperY.moveTo(desiredPos[1]);
        }

        if(stepperX.distanceToGo() == 0 && stepperY.distanceToGo() == 0 && toDesignatedPos){
          // reached the designated position
          reachedDesignatedPos = true;
          toDesignatedPos = false;
          if(!triggerSolenoid && (posIDX - 2) % 2 == 0){
            digitalWrite(SOLENOID_VALVE, HIGH);
            triggerSolenoid = true;
          }
        }

        steppers.run();
        break;
    }
  }
}

ISR(TIMER2_COMPA_vect) {
  _millis++;
  if (_millis % 1000 == 0){
    // 1 second
    digitalWrite(LED9, !digitalRead(LED9));
  }
}

ISR(TIMER2_COMPB_vect) {
  /*
  Status indication
  */
  _LEDBlink++;

  digitalWrite(LED10_DRAW, drawStatus);
  digitalWrite(LED7_BTURN, blackTurnStatus);
  digitalWrite(LED8_WTURN, whiteTurnStatus);
  digitalWrite(LED6_ERROR, errorStatus);
  if(_LEDBlink % 100 == 0){
    if(whiteWinStatus){
      digitalWrite(LED8_WTURN, !digitalRead(LED8_WTURN));
    }
    if(blackWinStatus){
      digitalWrite(LED7_BTURN, !digitalRead(LED7_BTURN));
    }
    if(illegalMoveStatus){
      digitalWrite(LED6_ERROR, !digitalRead(LED6_ERROR));
    }
  }

}

void loop() {
  while(Serial.available() > 0){
    processIncomingByte(Serial.read());
  }
}

unsigned long Millis(){
  return _millis;
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
  pinMode(LED1_ONOFF, OUTPUT); digitalWrite(LED1_ONOFF, LOW);
  pinMode(LED2_START, OUTPUT); digitalWrite(LED2_START, LOW);
  pinMode(LED3_SETHOME, OUTPUT); digitalWrite(LED3_SETHOME, LOW);
  pinMode(LED4_READY, OUTPUT); digitalWrite(LED4_READY, LOW);
  pinMode(LED5_RUNNING, OUTPUT); digitalWrite(LED5_RUNNING, LOW);
  pinMode(LED6_ERROR, OUTPUT); digitalWrite(LED6_ERROR, LOW);
  pinMode(LED7_BTURN, OUTPUT); digitalWrite(LED7_BTURN, LOW);
  pinMode(LED8_WTURN, OUTPUT); digitalWrite(LED8_WTURN, LOW);
  pinMode(LED9, OUTPUT); digitalWrite(LED9, LOW);
  pinMode(LED10_DRAW, OUTPUT); digitalWrite(LED10_DRAW, LOW);
}

void setupStepper(){
  stepperX.setMaxSpeed(maxSPS);
  stepperY.setMaxSpeed(maxSPS);
  
  stepperX.setAcceleration(maxSPS*20);
  stepperY.setAcceleration(maxSPS*20);

  steppers.addStepper(stepperX);
  steppers.addStepper(stepperY);
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
      switch((int) floor(idx / 4) % 2){
        case 0:
          boardState_row1 |= ((idx % 4) * 2) + 1;
          break;
        case 1:
          boardState_row1 |= ((idx % 4) * 2);
          break;
      }
    }
    if (mux2Val > MUX_THRESHOLD){
      switch((int) floor(idx / 4) % 2){
        case 0:
          boardState_row2 |= ((idx % 4) * 2) + 1;
          break;
        case 1:
          boardState_row2 |= ((idx % 4) * 2);
          break;
      }
    }

    if (idx % 4 == 3){
      boardState_buffer[(int) floor(idx / 4)] = boardState_row1;
      boardState_buffer[(int) floor(idx / 4) + 4] = boardState_row2;
      boardState_row1 = 0;
      boardState_row2 = 0;
    }
  }

  Serial.write(boardState_buffer, 8);
  Serial.write(DELIMITER);
}

void movementMapping(const char x, const char y){
  /*
  Move the stepper motors to the designated position
  */
  desiredPos[0] = x * movementGap;
  desiredPos[1] = y * movementGap;

  toDesignatedPos = true;
  reachedDesignatedPos = false;
}

void updateStatus(const char status){
  /*
  Update board's status
  From LSB to MSB
  0: draw
  1: white win
  2: black win
  4: black turn
  5: white turn
  6: error
  7: illegal move (blink, error led)
  */
  for(int i = 0; i < 8; i++){
    if (status & (1 << i)){
      switch(i){
        case 0:
          drawStatus = true;
          break;
        case 1:
          whiteWinStatus = true;
          break;
        case 2:
          blackWinStatus = true;
          break;
        case 4:
          blackTurnStatus = true;
          break;
        case 5:
          whiteTurnStatus = true;
          break;
        case 6:
          errorStatus = true;
          break;
        case 7:
          // illegal move (blink)
          illegalMoveStatus = true;
          break;
      }
    }
    else{
      switch(i){
        case 0:
          drawStatus = false;
          break;
        case 1:
          whiteWinStatus = false;
          break;
        case 2:
          blackWinStatus = false;
          break;
        case 4:
          blackTurnStatus = false;
          break;
        case 5:
          whiteTurnStatus = false;
          break;
        case 6:
          errorStatus = false;
          break;
        case 7:
          // illegal move (blink)
          illegalMoveStatus = false;
          break;
      }
    }
  }
}

void stateManagement(const byte mode, const char * data, const unsigned int dataLength){
  /*
  Process the data received from the Jetson
  */
  switch (connection){
    case DISCONNECTED:
      digitalWrite(LED1_ONOFF, LOW);
      switch (mode){
        case 0xF0:  // Connection request
          digitalWrite(LED1_ONOFF, HIGH);
          connection = CONNECTED;
          Serial.write(ACK);
          Serial.write(DELIMITER);
          break;
        default:
          Serial.write(NACK);
          Serial.write(DELIMITER);
          break;
      }
      break;
    
    case CONNECTED:
      switch(state){
        case IDLE:
          digitalWrite(LED4_READY, HIGH);

          // turn off the motors, to prevent overheating
          digitalWrite(DRV1_EN, LOW);
          digitalWrite(DRV2_EN, LOW);

          switch (mode){
            // Mode 0xF1: Requested for board state
            case 0xF1:
              Serial.write(ACK);
              Serial.write(DELIMITER);
              sendBoardData();
              _mode = mode;
              break;
            // Mode 0xF2: Requested for stepper movement
            case 0xF2:
              _mode = mode;
              _dataBuffer = data;
              _dataLength = dataLength;
              Serial.write(ACK);
              Serial.write(DELIMITER);
              state = MOTOR_RUNNING;
              break;
            // Mode 0xF3: Requested for status indication
            case 0xF3:
              updateStatus(data[0]);
              Serial.write(ACK);
              Serial.write(DELIMITER);
              break;
            // Mode 0xFF: Disconnection request
            case 0xFF:
              connection = DISCONNECTED;
              state = SETHOME_IDLE;
              Serial.write(ACK);
              Serial.write(DELIMITER);
              break;
            // invalid mode (unknown command, should not happen)
            default:
              Serial.write(NACK);
              Serial.write(DELIMITER);
              break;
          }
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
      mode_received = false;

      if(bufferIDX > 0){
        for (int i = 0; i < bufferIDX - 1; i++){
          calculatedChecksum ^= RxBuffer[i];
          dataBuffer[i] = RxBuffer[i];
        }
      }

      if (calculatedChecksum == checksum){
        if(isACK(mode)){
          receivedACK = true;
        }
        else{
          receivedACK = false;
        }
        // Checksum is correct, send ACK and process the data
        stateManagement(mode, dataBuffer, bufferIDX - 1);
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

bool isACK(const byte inByte){
  return inByte == ACK;
}