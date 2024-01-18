#ifndef CONTROLLER_H
#define CONTROLLER_H


#include "Device.h"

template<typename T>
class Controller : public Device<T> {
protected:
    template<typename Any>
    void _attachDevice(String tag, Device<Any> device);

public:
    Controller();
    int level();
    template<typename Any>
    void device(String tag, Device<Any> device);
    template<typename Any>
    Device<Any> device(String tag);
};


#endif // CONTROLLER_H
