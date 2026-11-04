/* Handwritten native test driver, not a generated code tab. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>

uint32_t multiply_by_repeated_addition(uint32_t x, uint32_t y);

static void check(uint32_t a, uint32_t b) {
  uint64_t expected = (uint64_t)a * b;
  assert(expected <= UINT32_MAX);
  assert(multiply_by_repeated_addition(a, b) == expected);
}

int main(void) {
  for (uint32_t a = 0; a <= 100; ++a)
    for (uint32_t b = 0; b <= 100; ++b)
      check(a, b);
  check(UINT32_MAX, 0);
  check(UINT32_MAX, 1);
  check(UINT32_MAX / 2, 2);
  check(65537, 65535);
  check(65536, 65535);
  check(0, 65535);
  puts("PAL annotated C: 10207 valid-input cases passed");
}
