/*!
*  @file Adafruit_BNO08x_RVC.cpp
*
*  @mainpage Adafruit BNO08x RVC A simple library to use the UART-RVC mode of
* the BNO08x sensors from Hillcrest Laboratories
*
*  @section intro_sec Introduction
*
* 	I2C Driver for the Library for the BNO08x_RVC A simple library to use
* the UART-RVC mode of the BNO08x sensors from Hillcrest Laboratories
*
* 	This is a library for the Adafruit BNO08x_RVC breakout:
* 	https://www.adafruit.com/product/4754
*
* 	Adafruit invests time and resources providing this open source code,
*  please support Adafruit and open-source hardware by purchasing products from
* 	Adafruit!
*
*  @section dependencies Dependencies
*  This library depends on the Adafruit BusIO library
*
*  This library depends on the Adafruit Unified Sensor library
*
*  @section author Author
*
*  Bryan Siepert for Adafruit Industries
*
* 	@section license License
*
* 	BSD (see license.txt)
*
* 	@section  HISTORY
*
*     v1.0 - First release
*/

#include "Arduino.h"
#include <Wire.h>

#include "Adafruit_BNO08x_RVC.h"

/**
* @brief Construct a new Adafruit_BNO08x_RVC::Adafruit_BNO08x_RVC object
*
*/
Adafruit_BNO08x_RVC::Adafruit_BNO08x_RVC(void) {}

/**
* @brief Destroy the Adafruit_BNO08x_RVC::Adafruit_BNO08x_RVC object
*
*/
Adafruit_BNO08x_RVC::~Adafruit_BNO08x_RVC(void) {}

/*!
*  @brief  Setups the hardware
*  @param  theSerial
*          Pointer to Stream (HardwareSerial/SoftwareSerial) interface
*  @return True
*/
bool Adafruit_BNO08x_RVC::begin(Stream *theSerial) {
   serial_dev = theSerial;
   return true;
}

/**
* @brief Get the next available heading and acceleration data from the sensor
*
* @param heading pointer to a BNO08x_RVC_Data struct to hold the measurements
* @return true: success false: failure
*/
bool Adafruit_BNO08x_RVC::read(BNO08x_RVC_Data *heading) {
   if (!heading) {
       return false;
   }

   if (!serial_dev->available()) {
       return false;
   }
   if (serial_dev->peek() != 0xAA) {
       serial_dev->read();
       return false;
   }
   // Now read all 19 bytes

   if (serial_dev->available() < 19) {
       return false;
   }
   // at this point we know there's at least 19 bytes available and the first
   if (serial_dev->read() != 0xAA) {
       // shouldn't happen baecause peek said it was 0xAA
       return false;
   }
   // make sure the next byte is the second 0xAA
   if (serial_dev->read() != 0xAA) {
       return false;
   }
   uint8_t buffer[19];
   // ok, we've got our header, read the actual data+crc
   if (!serial_dev->readBytes(buffer, 17)) {
       return false;
   };

   uint8_t sum = 0;
   // get checksum ready
   for (uint8_t i = 0; i < 16; i++) {
       sum += buffer[i];
   }
   if (sum != buffer[16]) {
       return false;
   }

   // The data comes in endian'd, this solves it so it works on all platforms
   int16_t buffer_16[6];

   for (uint8_t i = 0; i < 6; i++) {

       buffer_16[i] = (buffer[1 + (i * 2)]);
       buffer_16[i] += (buffer[1 + (i * 2) + 1] << 8);
   }
   heading->yaw = (float)buffer_16[0] * DEGREE_SCALE;
   heading->pitch = (float)buffer_16[1] * DEGREE_SCALE;
   heading->roll = (float)buffer_16[2] * DEGREE_SCALE;

   heading->x_accel = (float)buffer_16[3] * MILLI_G_TO_MS2;
   heading->y_accel = (float)buffer_16[4] * MILLI_G_TO_MS2;
   heading->z_accel = (float)buffer_16[5] * MILLI_G_TO_MS2;

   return true;
}