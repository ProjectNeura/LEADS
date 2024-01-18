#include "Device.h"

template<typename T>
Device<T>::Device(const int* pins)
  : _pins(pins) {
}
template<typename T>
void Device<T>::tag(String tag) {
  _tag = tag;
}
template<typename T>
String Device<T>::tag() {
  return _tag;
}
template<typename T>
void Device<T>::parentTags(String* parentTags) {
  _parentTags = new ArrayList<String>(parentTags);
}
template<typename T>
String* Device<T>::parentTags() {
  return _parentTags.toArray();
}
template<typename T>
void Device<T>::pinsCheck(int requiredNum) {
  if (sizeof(_pins) != requiredNum) throw value_error(format("This device only takes in {} pins", requiredNum));
}