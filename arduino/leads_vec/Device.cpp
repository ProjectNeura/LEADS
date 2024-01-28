#include "Device.h"

template<typename T>
Device<T>::Device(ArrayList<int> pins) : _pins(pins) {}
template<typename T>
void Device<T>::tag(String tag) {
    _tag = tag;
}
template<typename T>
String Device<T>::tag() {
    return _tag;
}
template<typename T>
void Device<T>::parentTags(ArrayList<String> parentTags) {
    _parentTags = parentTags;
}
template<typename T>
ArrayList<String> Device<T>::parentTags() {
    return _parentTags;
}
template<typename T>
void Device<T>::pinsCheck(int requiredNum) {
    if (sizeof(_pins) != requiredNum)
        throw value_error(format("This device only takes in {} pins", requiredNum));
}
bool pulse(int pin) { return digitalRead(pin) == LOW; }
