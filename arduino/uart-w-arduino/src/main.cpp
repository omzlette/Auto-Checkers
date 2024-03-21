#include <Arduino.h>
#include <Stepper.h>

// put function declarations here:
int data1, data2;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    data1 = Serial.readStringUntil(' ').toInt();
    data2 = Serial.readStringUntil('\n').toInt();
    Serial.print("Data1: ");
    Serial.println(data1);
    Serial.print("Data2: ");
    Serial.println(data2);

  }
}

// put function definitions here:
