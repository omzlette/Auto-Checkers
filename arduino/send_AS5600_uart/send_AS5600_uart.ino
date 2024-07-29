#include <Wire.h>
#include <AS5600.h>

const char DELIMITER = ';';
volatile unsigned long _millis = 0;
volatile long rawAngle = 0;
volatile bool sendData = false;

AS5600 as5600;   //  use default Wire

void setup() {
  cli();
    // 1kHz
  TCCR2A = 0;
  TCCR2B = 0;
  TCNT2  = 0;
  OCR2A = 249; // = (16*10^6) / prescaler / (1*10^3) - 1
  TCCR2A |= (1 << WGM21);
  TCCR2B |= (1 << CS22); // prescaler = 64
  TIMSK2 |= (1 << OCIE2A);

  pinMode(7, INPUT);

  // put your setup code here, to run once:
  Wire.begin();
  Wire.setClock(400000);

  // as5600.begin(4);  //  set direction pin.
  // as5600.setDirection(AS5600_CLOCK_WISE);  //  default, just be explicit.

  Serial.begin(115200);

  sei();
}

ISR(TIMER2_COMPA_vect) {
  _millis++;
  if(digitalRead(7)){
    sendData = true;
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  // Serial.print('<');
  // Serial.println(as5600.rawAngle());
  // Serial.print('>');
  // Serial.println();
  // delay(1);
  // Serial.println('a');
  rawAngle = as5600.rawAngle();

  if(sendData){
    Serial.write((uint8_t*)&rawAngle, sizeof(rawAngle));
    Serial.write((uint8_t*)&_millis, sizeof(_millis));
    sendData = false;
  }
}
