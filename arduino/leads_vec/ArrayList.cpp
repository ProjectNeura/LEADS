#include "ArrayList.h"

template<typename E>
ArrayList<E>::ArrayList(int initialCapacity) {
  if (initialCapacity > 0) {
    elementData = new E[initialCapacity];
  } else if (initialCapacity == 0) {
    elementData = {};
  } else {
    throw invalid_argument("Illegal Capacity: " + initialCapacity);
  }
}
template<typename E>
ArrayList<E>::ArrayList() {
  elementData = {};
}
template<typename E>
ArrayList<E>::ArrayList(E* initialArray) {
  if (initialArray.length > 0) elementData = initialArray;
  else elementData = {};
}
template<typename E>
void ArrayList<E>::add(E o) {
  grow(size + 1);
}