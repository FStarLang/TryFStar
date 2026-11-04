#load "fsharp/FStarCustard.fs"
#load "fsharp/Multiply.fs"

let check (a: uint32) (b: uint32) =
    let expected = uint64 a * uint64 b
    if expected > uint64 System.UInt32.MaxValue then
        failwith "The sample requires the product to fit in UInt32"
    let x = ref a
    let y = ref b
    Multiply.multiply_multiply x y
    if uint64 x.Value <> expected || y.Value <> b then
        failwithf "Multiplication failed for %u and %u" a b

for a in 0u .. 100u do
    for b in 0u .. 100u do
        check a b
for (a, b) in [(System.UInt32.MaxValue, 0u); (System.UInt32.MaxValue, 1u);
               (2147483647u, 2u); (65537u, 65535u); (65536u, 65535u); (0u, 65535u)] do
    check a b
printfn "F#: 10207 multiplication cases passed; y preserved"
