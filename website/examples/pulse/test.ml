(* Handwritten test driver, not an extracted code tab. *)
let check a b =
  let expected = Int64.mul a b in
  assert (expected <= 4294967295L);
  let x = ref (FStar_UInt32.of_string (Int64.to_string a)) in
  let y = ref (FStar_UInt32.of_string (Int64.to_string b)) in
  Multiply.multiply_multiply x y;
  assert (FStar_UInt32.to_string !x = Int64.to_string expected);
  assert (FStar_UInt32.to_string !y = Int64.to_string b)

let () =
  for a = 0 to 100 do
    for b = 0 to 100 do check (Int64.of_int a) (Int64.of_int b) done
  done;
  List.iter (fun (a, b) -> check a b)
    [4294967295L, 0L; 4294967295L, 1L; 2147483647L, 2L;
     65537L, 65535L; 65536L, 65535L; 0L, 65535L];
  print_endline "Custard OCaml: 10207 valid-input cases passed; y preserved"
