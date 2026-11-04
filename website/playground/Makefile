.DEFAULT_GOAL := help
PROJECTS := functional pulse pal pal-csharp

.PHONY: help setup doctor verify extract check tutorial-check serve
help:
	@printf '%s\n' \
	  'make check          Verify, extract, compile, and run every sample' \
	  'make verify         Verify the four projects' \
	  'make extract        Extract F* and Pulse to C, OCaml, and F#' \
	  'make -C pal check   Translate, verify, compile, and run annotated C' \
	  'make -C pal-csharp check  Translate, verify, and run annotated C#' \
	  'make tutorial-check Verify introductory F* and Pulse tutorial files' \
	  'make serve          Start the tutorial if needed; preview port 8000'

setup:
	python3 setup.py

doctor:
	@set -e; for tool in fstar.exe pal palcs clang-20 gcc-15 ocamlc ocamlfind dotnet; do command -v "$$tool"; done
	fstar.exe --version
	ocamlc -version
	dotnet --version

verify:
	@set -e; for project in $(PROJECTS); do $(MAKE) -C "$$project" verify; done

extract:
	$(MAKE) -C functional extract
	$(MAKE) -C pulse extract

check: doctor
	python3 -m unittest -q test_setup.py test_preview.py test_pal_csharp.py
	@set -e; for project in $(PROJECTS); do $(MAKE) -C "$$project" check; done
	$(MAKE) tutorial-check

tutorial-check:
	mkdir -p tutorials/_build/cache
	fstar.exe --cache_checked_modules --cache_dir tutorials/_build/cache \
	  tutorials/Part1.GettingOffTheGround.fst
	fstar.exe --cache_checked_modules --cache_dir tutorials/_build/cache \
	  --include tutorials/pulse tutorials/pulse/PulseTutorial.Intro.fst

serve:
	python3 preview.py
