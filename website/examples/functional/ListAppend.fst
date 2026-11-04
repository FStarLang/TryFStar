module ListAppend

open FStar.List.Tot

let rec list_append (x y:list 'a)
  : z:list 'a { length x + length y == length z }
  = match x with
    | [] -> y
    | hd :: tl -> hd :: list_append tl y

let append_u32 (x y:list FStar.UInt32.t) = list_append x y
