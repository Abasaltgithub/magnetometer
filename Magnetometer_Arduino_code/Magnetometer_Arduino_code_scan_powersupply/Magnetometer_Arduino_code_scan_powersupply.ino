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
int pwmValue = 0; // Initialize PWM duty cycle to 0

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

  // Set MOSFET pin (pin 9) as an output
  pinMode(9, OUTPUT);
  analogWrite(9, pwmValue); // Initialize PWM duty cycle
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    /* Or....get a new sensor event, normalized to uTesla */
    sensors_event_t event;
    lis3mdl.getEvent(&event);

    // Print only the normalized magnetic field values in uTesla
    Serial.print("X: "); Serial.print(event.magnetic.x); Serial.print(" uTesla\t");
    Serial.print("Y: "); Serial.print(event.magnetic.y); Serial.print(" uTesla\t");
    Serial.print("Z: "); Serial.print(event.magnetic.z); Serial.println(" uTesla");
  }

  // Check for commands from Python
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command >= '0' && command <= '9') {
      // Set PWM duty cycle based on the received command ('0' to '9')
      pwmValue = map(command - '0', 0, 9, 0, 255);
      analogWrite(9, pwmValue);
    }
  }
}
