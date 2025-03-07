/*!
*  @file Adafruit_BNO08x_RVC.h
*
* 	I2C Driver for the Adafruit BNO08x RVC A simple library to use the
*UART-RVC mode of the BNO08x sensors from Hillcrest Laboratories
*
* 	This is a library for use with thethe Adafruit BNO08x breakout:
* 	https://www.adafruit.com/products/4754
*
* 	Adafruit invests time and resources providing this open source code,
*  please support Adafruit and open-source hardware by purchasing products from
* 	Adafruit!
*
*
*	BSD license (see license.txt)
*/

#ifndef _ADAFRUIT_BNO08x_RVC_H
#define _ADAFRUIT_BNO08x_RVC_H

#define MILLI_G_TO_MS2 0.0098067 ///< Scalar to convert milli-gs to m/s^2
#define DEGREE_SCALE 0.01        ///< To convert the degree values

#include "Arduino.h"

/*!
*    @brief  Class that stores state and functions for interacting with
*            the BNO08x_RVC A simple library to use the UART-RVC mode of the
* BNO08x sensors from Hillcrest Laboratories
*/
/**! Struct to hold a UART-RVC packet **/
typedef struct BNO08xRVCData {
   float yaw,     ///< Yaw in Degrees
           pitch,     ///< Pitch in Degrees
           roll;      ///< Roll in Degrees
   float x_accel, ///< The X acceleration value in m/s^2
           y_accel,   ///< The Y acceleration value in m/s^2
           z_accel;   ///< The Z acceleration value in m/s^2

} BNO08x_RVC_Data;

/**
* @brief A class to interact with the BNO08x sensors from Hillcrest
* Laboritories using the UART-RVC mode
*
*/
class Adafruit_BNO08x_RVC {
public:
   Adafruit_BNO08x_RVC();
   ~Adafruit_BNO08x_RVC();

   bool begin(Stream *theStream);
   bool read(BNO08x_RVC_Data *heading);

private:
   Stream *serial_dev;
};

#endif