let () =
  assert (Custard.listAppend_list_append [] [1; 2] = [1; 2]);
  assert (Custard.listAppend_list_append [1; 2] [] = [1; 2]);
  assert (Custard.listAppend_list_append [1; 2] [3; 4] = [1; 2; 3; 4])
