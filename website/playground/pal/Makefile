.DEFAULT_GOAL := check
FSTAR_EXE ?= fstar.exe
PAL_ROOT ?= /opt/pal
FSTAR = $(FSTAR_EXE) --cache_checked_modules --cache_dir $(abspath _build/cache) \
  --already_cached Prims,FStar,Pulse.Nolib,Pulse.Class,Pulse.Lib,PulseCore \
  --include $(PAL_ROOT)/pulse --include $(PAL_ROOT)/pulse/_cache \
  --include $(abspath _build/pulse)
SOURCES = $(wildcard _build/pulse/*.fst _build/pulse/*.fsti)

-include _build/deps.mk

.PHONY: translate verify checked check
translate:
	mkdir -p _build/pulse _build/cache
	rm -f _build/pulse/*.fst _build/pulse/*.fsti _build/pulse/diagnostics.json
	pal --outdir _build/pulse multiply.c
	python3 -c 'import json; d=json.load(open("_build/pulse/diagnostics.json")); assert not d, d'

verify: translate
	$(FSTAR) --dep full $(SOURCES) --output_deps_to _build/deps.mk
	$(MAKE) checked

checked: $(ALL_CHECKED_FILES)

$(abspath _build/cache)/%.checked:
	$(FSTAR) $<

check: verify
	$(CC) -std=c11 -O2 -Wall -Wextra -Werror multiply.c test.c -o _build/test
	_build/test
	@echo 'PAL: translated C verified and native execution passed'
