#include "Algorithms.h"
#include "Arduino.h"

bool pulseTriggered(int pin) { return digitalRead(pin) == LOW; }

bool equivalent(float a, float b, float epsilon) {
    return fabs(a - b) <= epsilon * max(fabs(a), fabs(b));
}

bool equivalent(long a, long b, float epsilon) {
    return fabs(a - b) <= epsilon * max(fabs(a), fabs(b));
}
