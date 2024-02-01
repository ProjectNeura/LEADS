#ifndef DEVICE_H
#define DEVICE_H


#include "ArrayList.h"

template<typename T>
class Device {
protected:
    String _tag = "";
    ArrayList<String> _parentTags();
    int *const _pins;

public:
    Device(int *const pins) : _pins(pins) {}
    ~Device() {
        delete[] _pins;
    }
    void tag(String tag) {
        _tag = tag;
    }
    String tag() {
        return _tag;
    }
    void parentTags(ArrayList<String> parentTags) {
        _parentTags = parentTags;
    }
    ArrayList<String> parentTags() {
        return _parentTags;
    }
    void pinsCheck(int requiredNum) {
        if (sizeof(_pins) != requiredNum)
            throw value_error(format("This device only takes in {} pins", requiredNum));
    }
    void initialize(String *parentTags);
    T read();
    void write(T payload);
    void close();
};


#endif // DEVICE_H
