#include "LEADS.h"

const int PIN_VOT[] = {2};

VoltageSensor VOT(PIN_VOT);

void setup() {
    Serial.begin(9600);
    VOT.initialize();
}

void loop() {
    returnFloat("vot", VOT.read());
    delay(100);
}
