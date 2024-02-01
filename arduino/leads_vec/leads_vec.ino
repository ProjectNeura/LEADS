#include "Device.h"
// #include "ArrayList.h"
#include "Algorithms.h"

Device<int> a({2});
// ArrayList<int> a({2});

void setup() {
    Serial.begin(9600);
}

void loop() {
    Serial.println("A");
}
