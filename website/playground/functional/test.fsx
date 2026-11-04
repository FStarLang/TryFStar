#load "fsharp/FStarCustard.fs"
#load "fsharp/Custard.fs"

for (left, right) in [([], [1; 2]); ([1; 2], []); ([1; 2], [3; 4])] do
    let actual = Custard.listAppend_list_append left right
    if actual <> left @ right then
        failwithf "Append returned %A for %A and %A" actual left right
printfn "F#: append checks passed"
