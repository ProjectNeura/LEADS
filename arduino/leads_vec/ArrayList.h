#ifndef ARRAYLIST_H
#define ARRAYLIST_H


template<typename E>
class ArrayList {
private:
    E *_array = {};

public:
    ArrayList();
    ArrayList(int initialCapacity);
    ArrayList(E *initialArray);
    int size();
    E *toArray();
};


#endif // ARRAYLIST_H
