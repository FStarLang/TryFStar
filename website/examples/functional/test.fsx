#load "fsharp/FStarCustard.fs"
#load "fsharp/Custard.fs"

assert (Custard.listAppend_list_append [] [1; 2] = [1; 2])
assert (Custard.listAppend_list_append [1; 2] [] = [1; 2])
assert (Custard.listAppend_list_append [1; 2] [3; 4] = [1; 2; 3; 4])
