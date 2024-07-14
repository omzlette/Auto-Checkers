#include <Wire.h>
#include <AS5600.h>

#define DIR_PIN 2
#define BUTTON 13

AMS_5600 encoder;

bool startFlag = false;

volatile unsigned long now = 0;
volatile unsigned long last = 0;
volatile bool outputFlag = false;
volatile bool startDebug = false;

float mapfloat(long x, long in_min, long in_max, long out_min, long out_max)
{
  return (float)(x - in_min) * (out_max - out_min) / (float)(in_max - in_min) + out_min;
}

float Angle(){
  long in;
  in = mapfloat(encoder.getRawAngle(), 0, 4095, 0, 360);
  return in;
}

void output(long rawAngle){
  Serial.write((uint8_t*)&rawAngle, sizeof(rawAngle));
  Serial.write((uint8_t*)&now, sizeof(now));
  Serial.write(digitalRead(12));
  Serial.write(digitalRead(BUTTON));
}

void setup() {
  cli();
  //set timer0 interrupt at 1kHz
  TCCR0A = 0;// set entire TCCR0A register to 0
  TCCR0B = 0;// same for TCCR0B
  TCNT0  = 0;//initialize counter value to 0
  // set compare match register for 1khz increments
  OCR0A = 249;// = (16*10^6) / (1000*64) - 1 (must be <256)
  // turn on CTC mode
  TCCR0A |= (1 << WGM01);
  // Set CS01 and CS00 bits for 64 prescaler
  TCCR0B |= (1 << CS01) | (1 << CS00);   
  // enable timer compare interrupt
  TIMSK0 |= (1 << OCIE0A);

  pinMode(DIR_PIN, OUTPUT);
  pinMode(BUTTON, INPUT);
  pinMode(12, INPUT);
  Serial.begin(115200);
  Wire.begin();
  Wire.setClock(400000);

  sei();
}

ISR(TIMER0_COMPA_vect){
  now++;
  startDebug = digitalRead(12);
  if(startDebug){
    outputFlag = true;
  }
}

void loop() {
  if(outputFlag){
    outputFlag = false;
    output(encoder.getRawAngle());
    last = now;
  }
}