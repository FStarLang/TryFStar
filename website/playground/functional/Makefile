.DEFAULT_GOAL := check
FSTAR_EXE ?= fstar.exe
CHERRY_CC ?= gcc-15
FLAGS := --cache_checked_modules --cache_dir $(abspath _build/cache)

.PHONY: verify extract check
verify:
	mkdir -p _build/cache
	$(FSTAR_EXE) $(FLAGS) ListAppend.fst

extract: verify
	mkdir -p _build/ocaml _build/fsharp _build/cherry
	$(FSTAR_EXE) $(FLAGS) ListAppend.fst --codegen OCaml \
	  --custard_entry ListAppend.list_append -o $(abspath _build/ocaml/Custard.ml)
	$(FSTAR_EXE) $(FLAGS) ListAppend.fst --codegen FSharp \
	  --custard_entry ListAppend.list_append -o $(abspath _build/fsharp/Custard.fs)
	$(FSTAR_EXE) $(FLAGS) ListAppend.fst --codegen Cherry \
	  --custard_monomorphize_types true --custard_entry ListAppend.append_u32 \
	  -o $(abspath _build/cherry/ListAppend.c)

check: extract
	$(CHERRY_CC) -std=c11 -O2 -Wall -Wextra -Werror -I_build \
	  -I"$$($(FSTAR_EXE) --locate_lib)/ulib/c" \
	  test.c "$$($(FSTAR_EXE) --locate_lib)/ulib/c/cherry.c" -o _build/test-c
	_build/test-c
	cp test.ml _build/ocaml/test.ml
	cd _build/ocaml && ocamlc -o test Custard.ml test.ml && ./test
	dotnet build _build/fsharp/Custard.fsproj --verbosity quiet
	cp test.fsx _build/test.fsx
	dotnet fsi --exec _build/test.fsx
	@echo 'Functional F*: verification and C / OCaml / F# execution passed'
