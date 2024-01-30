#ifndef ARRAYLIST_H
#define ARRAYLIST_H


#include "Arduino.h"

template<typename E>
class ArrayList {
private:
    int _size;
    E *_array = {};
    void grow(size_t minCapacity) {
        int oldCapacity = _array.length;
        int newCapacity = oldCapacity + (oldCapacity >> 1);
        if (newCapacity < minCapacity) newCapacity = minCapacity;
        E newArray = new E[newCapacity];
        copy(begin(_array), end(_array), begin(newArray));
        _array = newArray;
    }
    void ensureExplicitCapacity(size_t minCapacity) {
        if (minCapacity > _array.length) grow(minCapacity);
    }
    void ensureCapacityInternal(size_t minCapacity) {
        if (_array.length == 0) minCapacity = max(10, minCapacity);
        ensureExplicitCapacity(minCapacity);
    }

public:
    ArrayList(size_t initialCapacity = 10) : _size(0), _array(new E[initialCapacity]) {}
    ArrayList(E *const initialArray) : _size(0), _array(initialArray) {}
    ~ArrayList() {
        delete[] _array;
    }
    int size() {
        return _size;
    }
    E *const &toArray() {
        return _array;
    }
    E get(int index) {
        return _array[index];
    }
    void add(E element) {
        ensureCapacityInternal(_size + 1);
        _array[_size++] = element;
    }
    bool insert(int index, E element);
    bool contains(E element) {
        return indexOf(element) >= 0;
    }
    int indexOfInRange(E element, int start, int stop) {
        for (int i = start; i < stop; i++) if (_array[i] == element) return i;
        return -1;
    }
    int indexOf(E element) {
        return indexOfInRange(element, 0, _size);
    }
    int lastIndexOfInRange(E element, int start, int stop) {
        for (int i = stop - 1; i >= start; i--) if (_array[i] == element) return i;
        return -1;
    }
    int lastIndexOf(E element) {
        return lastIndexOfInRange(element, 0, _size);
    }
};


#endif // ARRAYLIST_H
