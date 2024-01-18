template<typename E>
class ArrayList {
private:
  static const int DEFAULT_CAPACITY = 10;
  E* elementData;
  int s;
  static int calculateCapacity(E* elementData, int minCapacity);
  void ensureCapacityInternal(int minCapacity);
  void grow(int minCapacity);
public:
  ArrayList(int initialCapacity);
  ArrayList();
  ArrayList(E* c);
  int size();
  bool isEmpty();
  bool contains(E o);
  int indexOf(E o);
  int indexOfRange(E o, int start, int end);
  int lastIndexOf(E o);
  int lastIndexOfRange(E o, int start, int end);
  E* toArray();
  E get();
  void add(E o);
};