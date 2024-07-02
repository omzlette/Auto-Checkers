void setup(){
  pinMode(31, OUTPUT);
  pinMode(30, OUTPUT);
  pinMode(18, INPUT_PULLUP);
  pinMode(19, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(18), []{if(digitalRead(18) == 0){digitalWrite(31, HIGH);}}, FALLING);
  attachInterrupt(digitalPinToInterrupt(19), OFF, FALLING);

  Serial.begin(115200);
}

void loop(){
  digitalWrite(30, HIGH);
  delay(100);
  digitalWrite(30, LOW);
  delay(100);
}

void ON(){
  digitalWrite(31, HIGH);
}

void OFF(){
  if(digitalRead(19) == 0){
    Serial.println("OFF Pressed");
    digitalWrite(31, LOW);
  }
}

// void debug(){
//   if(DEBUG){
//     if(micros() - now >= timeDelay){
//       now = micros();

//       float deltaT = (now - last);

//       deltaDist_S1 = stepper1.distanceToGo();
//       currPos_S1 = stepper1.currentPosition();
//       vel_S1 = stepper1.speed();

//           Serial.print(currPos_S1);
//           Serial.print(",");
//           Serial.print(vel_S1);
//           Serial.print(",");
//           Serial.print(now);

//           Serial.print(",");
//           Serial.println(Started);

//       last = micros();
//     }
//   }
// }