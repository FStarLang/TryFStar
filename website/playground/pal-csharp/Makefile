.DEFAULT_GOAL := check
FSTAR_EXE ?= fstar.exe
PAL_CS_ROOT ?= /opt/pal-csharp
FSTAR = $(FSTAR_EXE) --cache_checked_modules --cache_dir $(abspath _build/cache) \
  --already_cached Prims,FStar,Pulse.Nolib,Pulse.Class,Pulse.Lib,PulseCore \
  --include $(PAL_CS_ROOT)/pulse --include $(PAL_CS_ROOT)/pulse/_cache \
  --include $(abspath _build/pulse)
SOURCES = $(wildcard _build/pulse/*.fst _build/pulse/*.fsti)

-include _build/deps.mk

.PHONY: translate verify checked check
translate:
	mkdir -p _build/pulse _build/cache
	rm -f _build/pulse/*.fst _build/pulse/*.fsti
	palcs -o _build/pulse InsertionSortSorted.cs

verify: translate
	$(FSTAR) --dep full $(SOURCES) --output_deps_to _build/deps.mk
	$(MAKE) checked

checked: $(ALL_CHECKED_FILES)

$(abspath _build/cache)/%.checked:
	$(FSTAR) $<

check: verify
	dotnet run --project Sort.csproj --verbosity quiet
	@echo 'PAL-CSharp: sortedness and permutation verified; native C# execution passed'
