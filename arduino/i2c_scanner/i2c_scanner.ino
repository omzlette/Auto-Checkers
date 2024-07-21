#include <Wire.h> 

void(* resetFunc) (void) = 0;

void setup()
{
  Wire.begin();
  Serial.begin(115200);
  Serial.println("\nI2C Scanner");
  while (!Serial); 
 
  
}
 
 
void loop()
{
  byte error, address;
  int nDevices;
 
  Serial.println("Scanning...");
 
  nDevices = 0;
  for(address = 1; address < 127; address++ )
  {
    // The i2c_scanner uses the return value of
    // the Write.endTransmisstion to see if
    // a device did acknowledge to the address.
    Wire.beginTransmission(address);
    Serial.println("HI1");
    error = Wire.endTransmission();
    Serial.println("HI2");
    if (error == 0)
    {
   
      Serial.print("Found I2C at 0x");
      if (address<16)
       
        Serial.print("0");
        Serial.println(address,HEX);
        
 
      nDevices++;
    }
    else if (error==4)
    {
      Serial.print("Unknown error at address 0x");
      if (address<16)
        Serial.print("0");
      Serial.println(address,HEX);
    }    
  }
  if (nDevices == 0)
    Serial.println("No I2C devices found\n");
  else
    delay(2000);
    Serial.println("Resetting....");
    delay(5000);           // wait 5 seconds for next scan
    resetFunc();
}