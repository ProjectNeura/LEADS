#ifndef DEVICE_H
#define DEVICE_H


#include "Arduino.h"
#include "ArrayList.h"

template<typename T>
class Device {
protected:
    String _tag = "";
    ArrayList<String> _parentTags = new ArrayList<String>();
    ArrayList<int> _pins = new ArrayList<int>();

public:
    Device(ArrayList<int> pins);
    void tag(String tag);
    String tag();
    void parentTags(ArrayList<String> parentTags);
    ArrayList<String> parentTags();
    void pinsCheck(int requiredNum);
    void initialize(String *parentTags);
    T read();
    void write(T payload);
    void close();
};
bool pulse(int pin);


#endif // DEVICE_H
