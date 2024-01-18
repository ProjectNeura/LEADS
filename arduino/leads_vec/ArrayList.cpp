#include "ArrayList.h"


template<typename E> ArrayList<E>::ArrayList(int initialCapacity) {
    _array = new E[initialCapacity];
}
template<typename E> ArrayList<E>::ArrayList(E *initialArray) {
    _array = initialArray;
}
