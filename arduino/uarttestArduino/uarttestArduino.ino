//#include <Arduino.h>
#include <Stepper.h>

// put function declarations here:
 int data1;
 int data2;
//char buffer[100];

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
//  Serial.println("UART Test Program");
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    data1 = Serial.readStringUntil('-').toInt();
    data2 = Serial.readStringUntil('-').toInt();
    Serial.print("Data1: ");
    Serial.print(data1);
    Serial.print("\n");
    Serial.print("Data2: ");
    Serial.print(data2);
    Serial.print("\n");
  }
}

// put function definitions here:
