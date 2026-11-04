module Multiply
#lang-pulse

open Pulse.Lib.Pervasives
module U32 = FStar.UInt32
open FStar.UInt32

// Multiply in place. A fractional permission allows reading, but not writing, y.
fn multiply (x y: ref U32.t)
  preserves live x
  preserves y |-> Frac 'p 'y
  requires pure (U32.fits (U32.v !x * U32.v 'y))
  ensures pure (U32.v !x == U32.v (old !x) * U32.v 'y)
{
  let n = !x;
  let m = !y;
  x := 0ul;
  let mut ctr = 0ul;
  while (!ctr < m)
    invariant live ctr ** live x
    invariant pure (U32.v !ctr <= U32.v m /\
                    U32.v !x == U32.v n * U32.v !ctr)
    decreases (U32.v m - U32.v !ctr)
  {
    x := !x + n;
    ctr := !ctr + 1ul;
  }
}
