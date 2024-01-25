#include "Controller.h"

template<typename T>
Controller<T>::Controller() : Device<T>() {}
template<typename T>
int Controller<T>::level() {
    return this._parentTags.size();
}
template<typename T>
void Controller<T>::_attachDevice(String tag, Device<String> device) {
    _devices.add(device);
}
