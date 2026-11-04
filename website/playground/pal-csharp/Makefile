.DEFAULT_GOAL := check
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
FSTAR_EXE ?= fstar.exe
PAL_CS_ROOT ?= /opt/pal-csharp
FSTAR = $(FSTAR_EXE) --cache_checked_modules --cache_dir $(abspath _build/cache) \
  --already_cached Prims,FStar,Pulse.Nolib,Pulse.Class,Pulse.Lib,PulseCore \
  --include $(PAL_CS_ROOT)/pulse --include $(PAL_CS_ROOT)/pulse/_cache \
  --include $(abspath _build/pulse)
SOURCES = $(wildcard _build/pulse/*.fst _build/pulse/*.fsti)

-include _build/deps.mk

.PHONY: translate verify checked editor-setup editor-check check
translate:
	mkdir -p _build/pulse _build/cache
	rm -f _build/pulse/*.fst _build/pulse/*.fsti
	palcs -o _build/pulse InsertionSortSorted.cs

verify: translate
	$(FSTAR) --dep full $(SOURCES) --output_deps_to _build/deps.mk
	$(MAKE) checked FSTAR_MESSAGES="--message_format json" 2>&1 | palcs report -o _build/pulse

checked: $(ALL_CHECKED_FILES)

$(abspath _build/cache)/%.checked:
	$(FSTAR) $(FSTAR_MESSAGES) $<

# Register the report with Roslyn before the first proof run.
editor-setup:
	@if [ ! -f "$(PAL_CS_ROOT)/src/Pal.Analyzers/bin/Release/netstandard2.0/Pal.Analyzers.dll" ]; then \
	  dotnet build "$(PAL_CS_ROOT)/src/Pal.Analyzers/Pal.Analyzers.csproj" \
	    -c Release --verbosity quiet --ignore-failed-sources -p:NuGetAudit=false; \
	fi
	mkdir -p _build/pulse
	@test -f _build/pulse/verification.txt || \
	  printf '%s\n' '# Not yet verified. Run make verify to check C# proofs.' > _build/pulse/verification.txt
	dotnet restore Pal.Editor.csproj --verbosity quiet --ignore-failed-sources

editor-check: editor-setup
	dotnet build Pal.Editor.csproj --no-restore --verbosity quiet

check: verify editor-check
	dotnet run --project Sort.csproj --verbosity quiet
	@echo 'PAL-CSharp: sortedness and permutation verified; native C# execution passed'
