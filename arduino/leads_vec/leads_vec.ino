#include "WheelSpeedSensor.h"
#include "Algorithms.h"

#define PIN_LFWSS 2
#define PIN_RFWSS 3
#define PIN_LRWSS 4
#define PIN_RRWSS 5
#define PIN_MRWSS 6

WheelSpeedSensor LFWSS = WheelSpeedSensor({PIN_LFWSS});
WheelSpeedSensor RFWSS = WheelSpeedSensor({PIN_RFWSS});
WheelSpeedSensor LRWSS = WheelSpeedSensor({PIN_LRWSS});
WheelSpeedSensor RRWSS = WheelSpeedSensor({PIN_RRWSS});

void setup() {
    LFWSS.initialize();
    RFWSS.initialize();
    LRWSS.initialize();
    RRWSS.initialize();
}

char *toCharArray(String str) {
    int len = str.length() + 1;
    char r[len];
    str.toCharArray(r, len);
    return r;
}

char *str(int n) {
    char r[16];
    itoa(n, r, 10);
    return r;
}

void loop() {
    Serial.println(LFWSS.debug());
}
