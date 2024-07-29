#include "LEADS.h"  // LEADS>=1.1.0

const int PIN_VOT[] = {A0};

Peer P{};
VoltageSensor VOT{30000.0, 7500.0, ArrayList<int>(PIN_VOT)};

void setup() {
    P.initializeAsRoot();
    VOT.initializeAsRoot();
}

void loop() {
    returnFloat(P, VOLTAGE_SENSOR, VOT.read());
    delay(100);
}
