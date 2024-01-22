#ifndef ARRAYLIST_H
#define ARRAYLIST_H


template<typename E>
class ArrayList {
private:
    int _size;
    E *_array = {};

public:
    ArrayList();
    ArrayList(int initialCapacity);
    ArrayList(E *initialArray);
    int size();
    E *const &toArray();
    E get(int index);
    bool add(E element);
    bool insert(int index, E element);
    bool contains(E element);
    int indexOfInRange(E element, int start, int end);
    int indexOf(E element);
    int lastIndexOfInRange(E element, int start, int end);
    int lastIndexOf(E element);
};


#endif // ARRAYLIST_H
