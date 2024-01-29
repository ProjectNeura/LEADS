#ifndef ARRAYLIST_H
#define ARRAYLIST_H


#include "Arduino.h"

template<typename E>
class ArrayList {
private:
    int _size;
    E *_array = {};
    void grow(size_t minCapacity);
    void ensureExplicitCapacity(size_t minCapacity);
    void ensureCapacityInternal(size_t minCapacity);

public:
    ArrayList(size_t initialCapacity = 10);
    ArrayList(E *const initialArray);
    ~ArrayList();
    int size();
    E *const &toArray();
    E get(int index);
    void add(E element);
    bool insert(int index, E element);
    bool contains(E element);
    int indexOfInRange(E element, int start, int stop);
    int indexOf(E element);
    int lastIndexOfInRange(E element, int start, int stop);
    int lastIndexOf(E element);
};


#endif // ARRAYLIST_H
