// #include <Wire.h>
// #include <AS5600.h>

// #define DIR_PIN 2
// #define BUTTON 13

// #define DEBUG_ERROR 8

// AMS_5600 encoder;

// bool startFlag = false;

// volatile unsigned long now = 0;
// volatile unsigned long last = 0;
// volatile bool outputFlag = false;
// volatile bool startDebug = false;

// void output(long rawAngle){
//   Serial.write((uint8_t*)&rawAngle, sizeof(rawAngle));
//   Serial.write((uint8_t*)&now, sizeof(now));
//   Serial.write(digitalRead(12)); // START MATCH 30
//   Serial.write(digitalRead(BUTTON)); // BUTTON 29
// }

// void setup() {
//   cli();
//   //set timer0 interrupt at 1kHz
//   TCCR2A = 0;// set entire TCCR0A register to 0
//   TCCR2B = 0;// same for TCCR0B
//   TCNT2  = 0;//initialize counter value to 0
//   // set compare match register for 1khz increments
//   OCR2A = 249;// = (16*10^6) / (1000*64) - 1 (must be <256)
//   // turn on CTC mode
//   TCCR2A |= (1 << WGM21);
//   // TCCR0B |= (1 << CS01) | (1 << CS00);   
//   TCCR2B |= (1 << CS22);
//   // enable timer compare interrupt
//   TIMSK2 |= (1 << OCIE2A);

//   pinMode(DIR_PIN, OUTPUT);
//   pinMode(BUTTON, INPUT);
//   pinMode(12, INPUT);
  
//   pinMode(DEBUG_ERROR, OUTPUT);

//   Serial.begin(115200);
//   Wire.begin();
//   Wire.setClock(400000);

//   sei();
// }

// ISR(TIMER2_COMPA_vect){
//   now++;
//   if(digitalRead(BUTTON)){
//     outputFlag = true;
//   }
//   digitalWrite(DEBUG_ERROR, digitalRead(BUTTON));
// }

// void loop(){
//   if(outputFlag){
//     outputFlag = false;
//     output(encoder.getRawAngle());
//   }
// }