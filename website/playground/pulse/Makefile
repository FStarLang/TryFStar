.DEFAULT_GOAL := check
FSTAR_EXE ?= fstar.exe
FLAGS := --cache_checked_modules --cache_dir $(abspath _build/cache)

.PHONY: verify extract check
verify:
	mkdir -p _build/cache
	$(FSTAR_EXE) $(FLAGS) Multiply.fst

extract: verify
	mkdir -p _build/c _build/ocaml _build/fsharp
	$(FSTAR_EXE) $(FLAGS) Multiply.fst --codegen C \
	  --custard_monomorphize_types true --custard_entry Multiply.multiply \
	  -o $(abspath _build/c/Multiply.c)
	$(FSTAR_EXE) $(FLAGS) Multiply.fst --codegen OCaml \
	  --custard_entry Multiply.multiply -o $(abspath _build/ocaml/Multiply.ml)
	$(FSTAR_EXE) $(FLAGS) Multiply.fst --codegen FSharp \
	  --custard_entry Multiply.multiply -o $(abspath _build/fsharp/Multiply.fs)

check: extract
	$(CC) -std=c11 -O2 -Wall -Wextra -Werror -I_build/c \
	  _build/c/Multiply.c test.c -o _build/test-c
	_build/test-c
	cp test.ml _build/ocaml/test.ml
	cp "$$($(FSTAR_EXE) --locate_lib)/lib/app/Prims.ml" _build/ocaml/
	cp "$$($(FSTAR_EXE) --locate_lib)/lib/app/ints/FStar_UInt32.ml" _build/ocaml/
	cd _build/ocaml && ocamlfind ocamlc \
	  -package stdint,zarith,ppx_deriving_yojson,ppx_deriving.show -linkpkg \
	  Prims.ml FStar_UInt32.ml Multiply.ml test.ml -o test && ./test
	dotnet build _build/fsharp/Multiply.fsproj --verbosity quiet
	cp test.fsx _build/test.fsx
	dotnet fsi --exec _build/test.fsx
	@echo 'Pulse: verification and C / OCaml / F# execution passed'
