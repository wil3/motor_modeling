//-------------------------------------------------------------------------------------
// HX711_ADC.h
// Arduino master library for HX711 24-Bit Analog-to-Digital Converter for Weigh Scales
// Olav Kallhovd sept2017
// Tested with      : HX711 asian module on channel A and YZC-133 3kg load cell
// Tested with MCU  : Arduino Nano
//-------------------------------------------------------------------------------------
// This is an example sketch on how to use this library for two ore more HX711 modules
// Settling time (number of samples) and data filtering can be adjusted in the config.h file

#include <HX711_ADC.h>
#include <EEPROM.h>

//HX711 constructor (dout pin, sck pin)
HX711_ADC LoadCell_1(5, 4); // Right Load Cell
HX711_ADC LoadCell_2(9, 7); // Left Load Cell
HX711_ADC LoadCell_3(11, 12); // Thrust Load Cell

const int eepromAdress_1 = 0; // eeprom adress for calibration value load cell 1 (4 bytes)
const int eepromAdress_2 = 4; // eeprom adress for calibration value load cell 2 (4 bytes)
const int eepromAdress_3 = 8; 

const int photoPin = 2;
volatile unsigned long count = 0;

double t;

void pulse() {
  count++;
} // end pulse

void setup() {
  
  float calValue_1; // calibration value load cell 1
  float calValue_2; // calibration value load cell 2
  float calValue_3; // calibration value load cell 3
  
  calValue_1 = 1;//696.0; // uncomment this if you want to set this value in the sketch 
  calValue_2 = 1;//733.0; // uncomment this if you want to set this value in the sketch 
  calValue_3 = 1;
  
  #if defined(ESP8266) 
  //EEPROM.begin(512); // uncomment this if you use ESP8266 and want to fetch the value from eeprom
  #endif
  //EEPROM.get(eepromAdress_1, calValue_1); // uncomment this if you want to fetch the value from eeprom
  //EEPROM.get(eepromAdress_2, calValue_2); // uncomment this if you want to fetch the value from eeprom
  
  Serial.begin(9600); delay(10);
  LoadCell_1.begin();
  LoadCell_2.begin();
  LoadCell_3.begin();
  
  long stabilisingtime = 2000; // tare preciscion can be improved by adding a few seconds of stabilising time
  byte loadcell_1_rdy = 0;
  byte loadcell_2_rdy = 0;
  byte loadcell_3_rdy = 0;
  while ((loadcell_1_rdy + loadcell_2_rdy + loadcell_3_rdy) < 3) { //run startup, stabilization and tare, both modules simultaniously
    if (!loadcell_1_rdy) loadcell_1_rdy = LoadCell_1.startMultiple(stabilisingtime);
    if (!loadcell_2_rdy) loadcell_2_rdy = LoadCell_2.startMultiple(stabilisingtime);
    if (!loadcell_3_rdy) loadcell_3_rdy = LoadCell_3.startMultiple(stabilisingtime);
  }
  
  LoadCell_1.setCalFactor(calValue_1); // user set calibration value (float)
  LoadCell_2.setCalFactor(calValue_2); // user set calibration value (float)
  LoadCell_3.setCalFactor(calValue_3);

  // Setup of Phototransistor
  pinMode(photoPin, INPUT);
  attachInterrupt(digitalPinToInterrupt(photoPin), pulse, CHANGE);

  // Initialize t here
  t = millis();
}

void loop() {
  //update() should be called at least as often as HX711 sample rate; >10Hz@10SPS, >80Hz@80SPS
  //longer delay in scetch will reduce effective sample rate (be carefull with use of delay() in the loop)
  LoadCell_1.update();
  LoadCell_2.update();
  LoadCell_3.update();

  //get smoothed value from data set + current calibration factor
  double currentTime = millis();
  if (currentTime > t + 50) {
    float a = LoadCell_1.getData();
    float b = LoadCell_2.getData();
    float c = LoadCell_3.getData();

    // Because of the way we need to sense the voltages, we're using CHANGE for the interrupt. That means there's an extra factor of 2 we need to account for,
    // and (if you do the math out) that's why it's 10,000 and not 20,000.
    float d = 10000 * (count / (currentTime - t)); 

    // Print format: <Thrust Load Cell> <TAB> <Left Load Cell> <TAB> <Right Load Cell> <TAB> <Phototransistor>
    Serial.print(c);
    Serial.print("  ");
    Serial.print(b);
    Serial.print("  ");
    Serial.print(a);
    Serial.print("  ");
    Serial.print(count);
    Serial.print("  ");
    Serial.println(d); 

    // Indexing
    t = millis();
    count = 0;
  }

  //receive from serial terminal
  if (Serial.available() > 0) {
    float i;
    char inByte = Serial.read();
    if (inByte == 't') {
      LoadCell_1.tareNoDelay();
      LoadCell_2.tareNoDelay();
      LoadCell_3.tareNoDelay();
    }
  }

  //check if last tare operation is complete
  if (LoadCell_1.getTareStatus() == true) {
    Serial.println("Tare load cell 1 complete");
  }
  if (LoadCell_2.getTareStatus() == true) {
    Serial.println("Tare load cell 2 complete");
  }
  if (LoadCell_3.getTareStatus() == true) {
    Serial.println("Tare load cell 3 complete");
  }

}
