/* Handwritten test driver, not an extracted code tab. */
#include "Multiply.h"
#include <assert.h>
#include <stdio.h>

static void check(uint32_t a, uint32_t b) {
  uint64_t expected = (uint64_t)a * b;
  assert(expected <= UINT32_MAX);
  uint32_t x = a, y = b;
  Multiply_multiply(&x, &y);
  assert(x == expected && y == b);
}

int main(void) {
  for (uint32_t a = 0; a <= 100; ++a)
    for (uint32_t b = 0; b <= 100; ++b)
      check(a, b);
  check(UINT32_MAX, 0);
  check(UINT32_MAX, 1);
  check(UINT32_MAX / 2, 2);
  check(65537, 65535); /* exact UINT32_MAX */
  check(65536, 65535); /* near the overflow boundary */
  check(0, 65535);
  puts("Custard C: 10207 valid-input cases passed; y preserved");
}
