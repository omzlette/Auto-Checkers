#include <Stepper.h>
#include <CD74HC4067.h>
// Define PINS
#define MUX_S0 4
#define MUX_S1 5
#define MUX_S2 6
#define MUX_S3 7
#define MUX_SIG A0
// Declare Variables
float muxVal[16] = {};
CD74HC4067 muxLogPINS(MUX_S0, MUX_S1, MUX_S2, MUX_S3);

void setup() {
  // put your setup code here, to run once:
  pinMode(MUX_SIG, INPUT);
  Serial.begin(115200);

}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.print("All Value: ");
  for(int idx = 0; idx < 4; idx++){
    muxLogPINS.channel(idx);
    muxVal[idx] = analogRead(MUX_SIG);
    Serial.print(muxVal[idx]);
    Serial.print(' ');
  }
  
  Serial.println();

}
