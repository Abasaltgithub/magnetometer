#include <Wire.h>
#include <Adafruit_LIS3MDL.h>
#include <Adafruit_Sensor.h>

Adafruit_LIS3MDL lis3mdl;
#define LIS3MDL_CLK 4
#define LIS3MDL_MISO 12
#define LIS3MDL_MOSI 11
#define LIS3MDL_CS 10

unsigned long previousMillis = 0;
const unsigned long interval = 50;

void setup(void) {
  Serial.begin(115200);
  while (!Serial) {
    delay(1000); // Wait for serial port to connect
  }
  Serial.println("Adafruit LIS3MDL test!");

  // Try to initialize the LIS3MDL sensor
  if (!lis3mdl.begin_SPI(LIS3MDL_CS, LIS3MDL_CLK, LIS3MDL_MISO, LIS3MDL_MOSI)) { // soft SPI
    Serial.println("Failed to find LIS3MDL chip");
    while (1) { delay(10); }
  }
  Serial.println("LIS3MDL Found!");

  // Set up LIS3MDL sensor configuration
  lis3mdl.setPerformanceMode(LIS3MDL_MEDIUMMODE);
  lis3mdl.setOperationMode(LIS3MDL_CONTINUOUSMODE);
  lis3mdl.setDataRate(LIS3MDL_DATARATE_155_HZ);
  lis3mdl.setRange(LIS3MDL_RANGE_16_GAUSS); // Set to the maximum ±16 gauss (±1600 µT) full scale;
  lis3mdl.setIntThreshold(500);
  lis3mdl.configInterrupt(false, false, true, true, false, true);

  // Set the digital output pin (e.g., digital pin 6) as an output
  pinMode(6, OUTPUT);
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    /* Or....get a new sensor event, normalized to uTesla */
    sensors_event_t event;
    lis3mdl.getEvent(&event);

    // Print the normalized magnetic field values in uTesla
    Serial.print("X: "); Serial.print(event.magnetic.x); Serial.print(" uTesla\t");
    Serial.print("Y: "); Serial.print(event.magnetic.y); Serial.print(" uTesla\t");
    Serial.print("Z: "); Serial.print(event.magnetic.z); Serial.println(" uTesla");

    // Output the Y-axis value (By) on digital pin 6
    int ByValue = map(event.magnetic.y, -1600, 1600, 0, 255);

    if (ByValue > 127) {
      digitalWrite(6, HIGH); // Set the pin HIGH
    } else {
      digitalWrite(6, LOW); // Set the pin LOW
    }
  }
}
