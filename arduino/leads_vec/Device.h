#ifndef DEVICE_H
#define DEVICE_H


#include "Arduino.h"
#include "ArrayList.h"

template<typename T>
class Device {
protected:
    String _tag = "";
    ArrayList<String> _parentTags = new ArrayList<String>();
    int *_pins;

public:
    Device(const int *pins);
    void tag(String tag);
    String tag();
    void parentTags(String *parentTags);
    String *parentTags();
    void pinsCheck(int requiredNum);
    void initialize(String *parentTags);
    T read();
    void write(T payload);
    void close();
};


#endif // DEVICE_H
