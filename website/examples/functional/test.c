#include <assert.h>
#include "cherry/ListAppend.c"

static Prims_list__uint32 sequence(uint32_t n) {
  Prims_list__uint32 result = CHERRY_SCALAR(PRIMS_NIL__UINT32);
  while (n > 0) {
    result = cherry_new_Prims_list__uint32_Cons(n, result);
    --n;
  }
  return result;
}

int main(void) {
  Prims_list__uint32 nil = CHERRY_SCALAR(PRIMS_NIL__UINT32);
  Prims_list__uint32 y = cherry_new_Prims_list__uint32_Cons(7,
    cherry_new_Prims_list__uint32_Cons(8, nil));
  Prims_list__uint32 empty = ListAppend_append_u32(nil, y);
  assert(empty == y);
  cherry_dec_Prims_list__uint32(empty);

  Prims_list__uint32 x = sequence(1000000);
  Prims_list__uint32 result = ListAppend_append_u32(x, y);
  assert(result == x);
  Prims_list__uint32 cursor = result;
  for (uint32_t i = 1; i <= 1000000; ++i) {
    assert(cherry_tag(cursor) == PRIMS_CONS__UINT32);
    struct Prims_list__uint32_Cons_s *cell = (struct Prims_list__uint32_Cons_s *)cursor;
    assert(cell->hd == i);
    cursor = cell->tl;
  }
  assert(cursor == y);
  cherry_dec_Prims_list__uint32(result);

  x = sequence(3);
  cherry_inc(x);
  result = ListAppend_append_u32(x, y);
  assert(result != x);
  assert(((struct Prims_list__uint32_Cons_s *)x)->hd == 1);
  cherry_dec_Prims_list__uint32(result);
  cherry_dec_Prims_list__uint32(x);
  cherry_dec_Prims_list__uint32(y);
  return 0;
}
