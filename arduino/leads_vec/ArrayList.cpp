#include "ArrayList.h"


template<typename E>
ArrayList<E>::ArrayList(int initialCapacity) {
    _array = new E[initialCapacity];
}
template<typename E>
ArrayList<E>::ArrayList(E *const initialArray) {
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
template<typename E>
E ArrayList<E>::get(int index) {
    return _array[index];
}
template<typename E>
void ArrayList<E>::grow(int minCapacity) {
    int oldCapacity = _array.length;
    int newCapacity = oldCapacity + (oldCapacity >> 1);
    if (newCapacity < minCapacity) newCapacity = minCapacity;
    E newArray = new E[newCapacity];
    copy(begin(_array), end(_array), begin(newArray));
    _array = newArray;
}
template<typename E>
void ArrayList<E>::ensureExplicitCapacity(int minCapacity) {
    if (minCapacity > _array.length) grow(minCapacity);
}
template<typename E>
void ArrayList<E>::ensureCapacityInternal(int minCapacity) {
    if (_array.length == 0) minCapacity = max(10, minCapacity);
    ensureExplicitCapacity(minCapacity);
}
template<typename E>
void ArrayList<E>::add(E element) {
    ensureCapacityInternal(_size + 1);
    _array[_size++] = element;
}
template<typename E>
bool ArrayList<E>::contains(E element) {
    return indexOf(element) >= 0;
}
template<typename E>
int ArrayList<E>::indexOfInRange(E element, int start, int stop) {
    for (int i = start; i < stop; i++) if (_array[i] == element) return i;
    return -1;
}
template<typename E>
int ArrayList<E>::indexOf(E element) {
    return indexOfInRange(element, 0, _size);
}
template<typename E>
int ArrayList<E>::lastIndexOfInRange(E element, int start, int stop) {
    for (int i = stop - 1; i >= start; i--) if (_array[i] == element) return i;
    return -1;
}
template<typename E>
int ArrayList<E>::lastIndexOf(E element) {
    return lastIndexOfInRange(element, 0, _size);
}
