#include "pal.h"
#include <stdint.h>

/* The casts make specifications mathematical, not wrapping C arithmetic. */
uint32_t multiply_by_repeated_addition(uint32_t x, uint32_t y)
  _requires((_specint) x * y <= UINT32_MAX)
  _ensures((_specint) return == (_specint) x * y)
{
  uint32_t ctr = 0;
  uint32_t acc = 0;
  while (ctr < y)
    _invariant(_live(ctr) && _live(acc))
    _invariant(ctr <= y && (_specint) acc == (_specint) x * ctr)
  {
    _assert((_specint) acc + x <= UINT32_MAX);
    _assert((_specint) ctr + 1 <= UINT32_MAX);
    acc = acc + x;
    ctr = ctr + 1;
  }
  return acc;
}
