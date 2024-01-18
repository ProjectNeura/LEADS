#include "ArrayList.h"

template<typename E>
ArrayList<E>::ArrayList(int initialCapacity) {
  if (initialCapacity > 0) {
    elementData = new E[initialCapacity];
  } else if (initialCapacity == 0) {
    elementData = EMPTY_ELEMENTDATA;
  } else {
    throw invalid_argument("Illegal Capacity: " + initialCapacity);
  }
}
template<typename E>
ArrayList<E>::ArrayList() {
  elementData = DEFAULTCAPACITY_EMPTY_ELEMENTDATA;
}
template<typename E>
ArrayList<E>::ArrayList(E* initialArray) {
  if (initialArray.length > 0) elementData = initialArray;
  else elementData = EMPTY_ELEMENTDATA;
}
template<typename E>
int ArrayList<E>::calculateCapacity(E* elementData, int minCapacity) {
}