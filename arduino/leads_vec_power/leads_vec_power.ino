#include "LEADS.h"
#include "Paddle.h"

const int PIN_VOT[] = {A0};

VoltageSensor VOT(30000.0, 7500.0, PIN_VOT);

void setup() {
    Serial.begin(9600);
    VOT.initialize();
}

void loop() {
    returnFloat(VOLTAGE_SENSOR, VOT.read());
    delay(100);
}
