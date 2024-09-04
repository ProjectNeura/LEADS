#include "LEADS.h"

const int PIN_VOT[] = {A0};

Peer P{POWER_CONTROLLER};
VoltageSensor VOT{ArrayList<int>(PIN_VOT, 1), 30000.0, 7500.0};

void setup() {
    P.initializeAsRoot();
    VOT.initializeAsRoot();
}

void loop() {
    P.refresh();
    returnFloat(P, VOLTAGE_SENSOR, VOT.read());
    delay(100);
}
