#include "ArrayList.h"

template<typename E>
ArrayList<E>::ArrayList(int initialCapacity) {
  if (initialCapacity > 0) {
    this.elementData = new E[initialCapacity];
  } else if (initialCapacity == 0) {
    this.elementData = EMPTY_ELEMENTDATA;
  } else {
    throw invalid_argument("Illegal Capacity: " + initialCapacity);
  }
}