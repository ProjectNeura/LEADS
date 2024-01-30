#include "Algorithms.h"
#include "Arduino.h"

bool pulseTriggered(int pin) { return digitalRead(pin) == LOW; }
