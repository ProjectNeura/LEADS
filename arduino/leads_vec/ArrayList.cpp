#include "ArrayList.h"


template<typename E>
ArrayList<E>::ArrayList(int initialCapacity) {
    _array = new E[initialCapacity];
}
template<typename E>
ArrayList<E>::ArrayList(E *initialArray) {
    _array = initialArray;
}
template<typename E>
int ArrayList<E>::size() {
    return _size;
}
template<typename E>
E *const &ArrayList<E>::toArray() {
    return _array;
}
