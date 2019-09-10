#include <iostream>
int main() {
  int *a = (int*)malloc(sizeof(int));
  int *b = (int*)malloc(sizeof(int));
  short *c = (short*)malloc(sizeof(short));
  std::cout << a << std::endl
            << b << std::endl
            << c << std::endl;
  std::cout << b - reinterpret_cast<size_t>(a) << std::endl;
  std::cout << reinterpret_cast<size_t>(b) - reinterpret_cast<size_t>(a) << std::endl;
}