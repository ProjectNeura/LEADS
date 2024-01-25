#ifndef CONTROLLER_H
#define CONTROLLER_H


#include "Device.h"

template<typename T>
class Controller : public Device<T> {
protected:
    ArrayList<Device<String>> _devices;
    void _attachDevice(String tag, Device<String> device);

public:
    Controller();
    int level();
    void device(String tag, Device<String> device);
    Device<String> device(String tag);
};


#endif // CONTROLLER_H
