#include "Arduino.h"

class Device {
protected:
  String tag = "";
  int* pins;
public:
  Device(const int* pins);
};