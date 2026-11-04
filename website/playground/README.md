# Try F*

An editable playground for the examples on the F* website. The named
devcontainer in `.devcontainer/try-fstar/` pulls a prebuilt image with F*, Pulse,
PAL, PAL-CSharp, their verified support libraries, and the C, OCaml, F#, and
.NET toolchains.
It uses a binary F* release, not a local build of this repository.

## Open the environment

In VS Code, open the repository and run **Dev Containers: Reopen in Container**,
then select **Try F*: Pulse, PAL, and PAL-CSharp**. Docker and the Dev Containers
extension must be installed locally. This image targets Linux x86-64.

In GitHub, use the [browser launch link](https://codespaces.new/FStarLang/TryFStar?quickstart=1&devcontainer_path=.devcontainer%2Ftry-fstar%2Fdevcontainer.json),
or **Code > Codespaces > New with options**, and select the same devcontainer
configuration. Choose at least 4 cores, 8 GB RAM, and 32 GB disk.
The initial launch downloads the image; it does not compile the toolchains
or translator executables. With the current older image pin, setup builds only
the small PAL-CSharp editor analyzer once per container, using cached packages
(about five seconds). Subsequent starts reuse it. The image's immutable registry
digest is pinned in `devcontainer.json`.

Setup opens this directory, copies editable source and test files from the
website examples, copies the tutorial sources, and runs `make doctor`. The image
has already passed `make check`; run it yourself to repeat the verification,
extraction, compilation, and runtime checks in your editable workspace. Existing
files are never overwritten, including your edits. VS Code includes the F*
assistant, C/C++, C#, F#, and build tasks for each project.
Copied sources initially appear as untracked files. Commit the sources and
solutions you want to keep before deleting a Codespace; build outputs and
machine-specific editor configurations are ignored.

## Explore

| Directory | Source | Check |
|---|---|---|
| `functional/` | Length-preserving list append in F* | Verify; extract to reference-counted C, OCaml, and F#; compile and run |
| `pulse/` | Repeated-addition multiplication in Pulse | Verify; extract to C, OCaml, and F#; compile and run |
| `pal/` | Annotated C multiplication | Translate to Pulse; verify; compile and run the original C |
| `pal-csharp/` | Annotated C# insertion sort | Translate to Pulse; prove sortedness, permutation, and preserved length; run the original C# |
| `tutorials/` | F* and Pulse tutorial sources, exercises, and solutions | Start with `Part1.GettingOffTheGround.fst` or `pulse/PulseTutorial.Intro.fst` |

```sh
make check                       # All four projects and introductory tutorials
make -C functional verify        # Only check a proof
make -C pulse extract            # Inspect generated code in pulse/_build/
make -C pal check                # Edit multiply.c, then retranslate and verify
make -C pal-csharp check         # Edit InsertionSortSorted.cs, then check it
```

Each project has its own Makefile and source/test files. You can copy a project
outside this repository and run it with this image or equivalent installed tools.
Generated code, verification caches, binaries, and .NET intermediates live in
`_build/`. The PAL projects use F*'s dependency graph to check **all** translated
modules, including newly added functions, rather than a fixed module list.
Verification does not use admitted queries or lax checking.

The Pulse and C examples require their mathematical product to fit in `uint32`.
The Pulse example proves termination; PAL currently translates the C function
as divergent, so its successful verification does not establish termination.
Runtime tests complement the proofs; they do not prove that the extraction or
translation tools themselves are correct.

Tutorial exercises intentionally include holes and expected errors.
`make tutorial-check` checks two introductory modules, not every unfinished
exercise. When first copying `PulseTutorial.Intro.fst`, setup applies the
small patch in `tutorial-compat/`: `par` and `par_incr` are explicitly
`divergent`, matching this release's parallel-composition API. Their heap
preconditions and postconditions are unchanged; these two parallel examples
do not promise termination. Other tutorial files are copied verbatim.
The bundled tutorial starts automatically when the editor attaches. Port **8000**
opens the book in an editor preview beside your code; the server's root URL
redirects straight to `/tutorial/book/`. Open the corresponding editable sources
under `tutorials/` in the other editor group. To reopen the book, right-click
port **8000** in the **Ports** panel and select **Preview in Editor**.
Outside the devcontainer, `make serve` starts the same server; if it is already
running, the command reports that rather than starting a duplicate.
Startup errors are reported by the lifecycle command, with the server log
under `/tmp/tryfstar-tutorial-*.log`.
In Codespaces, GitHub CLI makes **only this documentation port public** before
the server starts listening. This avoids GitHub's private-port authentication
redirect, which cannot be displayed inside Simple Browser. The document root
is restricted to `website/tutorial/book/`; project files, directory listings,
and symbolic links outside the book are not served. Other ports are unchanged.
No access token is put in the browser URL or page.
If organization policy prohibits public ports, the lifecycle command reports
the failure. To read privately in an external browser instead, run
`python3 -m http.server 8001 --bind 0.0.0.0 --directory ../tutorial/book`,
then open port **8001** using **Open in Browser**, not Simple Browser.
This serves the static book, not the legacy PHP-backed web verifier.
Source verification happens in the editor or terminal.

## PAL in the editor

The devcontainer enables `fstarVSCodeAssistant.c2pulse`. Setup creates
`pal/pal.config.json`, selecting `multiply.c` and writing generated Pulse files
to `_build/pulse`, alongside the existing F* project configuration. The assistant
uses `pal` on `PATH`; the native `test.c` harness is not translated.
C files keep their normal C language mode and C/C++ tooling.

Open `pal/multiply.c`, run **F*: Verify all** from the Command Palette once
to activate the assistant, then save the file. The published assistant
(0.25.4) auto-activates for F* files, but not C files alone. After activation,
saving runs PAL and verifies its generated modules; diagnostics and verification
status are mapped back to the C source. Unsaved C edits are not translated.
Use the Command Palette for F* commands in C files: the extension's default
F* keyboard shortcuts apply only in F* language mode.

For an existing Codespace, pull the latest repository changes and run
`python3 setup.py` from this directory. Add
`"fstarVSCodeAssistant.c2pulse": true` through **Preferences: Open Workspace
Settings (JSON)**, then run **Developer: Reload Window** before activating
the assistant. This setting is supported even though version 0.25.4 does not
list it in the Settings UI. Alternatively, rebuild the container to apply
the updated devcontainer defaults; the prebuilt verification toolchain is reused.
Setup preserves existing source files and editor configurations.

## PAL-CSharp in the editor

Open `pal-csharp/InsertionSortSorted.cs` in its normal C# language mode.
The Microsoft C# extension loads `TryFStar.sln` and `Pal.Editor.csproj`,
which use PAL-CSharp's own Roslyn analyzer. Translation and specification
diagnostics appear as you type, including errors inside attribute strings.
The ordinary `Test.cs` runtime harness is deliberately excluded from this
editor project; `Sort.csproj` still compiles and runs it as stock C#.

Save your changes, then use **Tasks: Run Task > PAL-CSharp: verify C# proofs**,
or run:

```sh
make -C pal-csharp verify
```

This translates the annotated C#, checks every generated module with F*, and
runs `palcs report` to map proof failures back to C#. The analyzer reads
`_build/pulse/verification.txt` and displays those failures as `PALCS0600`
diagnostics on the original source. A repaired proof clears the previous
failures when you rerun the task. Unmapped errors remain in the task output,
and a failed proof still fails the task.

Unlike PAL C, C# does not go through the F* assistant's C frontend: proof
checking is an explicit task, not automatic verification on save. The live
analyzer checks translatability, not proofs; proof diagnostics describe the
last verification run, not unsaved edits. No diagnostics does not by itself
mean a proof has run.

To update an existing Codespace, pull `main` and run **Codespaces: Rebuild
Container**. This applies the solution and file-watcher settings: the proof
report must be watched even though the other build caches are excluded.
Select `TryFStar.sln` if the C# extension asks which solution to open.
Setup preserves learner edits and builds the missing analyzer from the
pinned sources and cached packages; it does not rebuild F* or the translator
executables. Future source-built images preload the analyzer too.

## Toolchain pins

The Dockerfile is the source of truth for versions and download checksums:

- F*/Pulse: `FStarLang/FStar-nightly`, `nightly-2026-11-03`.
- PAL: `7b3915e03090394718f1ffb771c2b92f21563247`.
- PAL-CSharp: `3a6c05e15ea21f65ec5e66fe177305b135a7ce42`.
- .NET SDK 10.0.100, Rust 1.94.0, OCaml 5.3.0, LLVM/Clang 20, GCC 15.

GCC 15 is required for Cherry's guaranteed tail calls; those checks are not
disabled to build with an older compiler. Clang 20 builds PAL and the other C
examples. GCC comes from Ubuntu's signed toolchain PPA and LLVM from its
signed upstream apt repository.
The Pulse project compiles the release's original OCaml runtime bindings
alongside the extracted code. It does not assume that the distributor's
precompiled `fstar.cma` has the same OCaml standard-library ABI.

The PAL-CSharp snapshot deliberately precedes its dependency on unreleased
native Pulse exception support, allowing both translators to share a released
binary toolchain. The .NET and Rust base images are pinned by digest, F*'s
archive is checked against SHA-256, and translator source is pinned by commit.
Ubuntu, opam, and NuGet package repositories are not snapshotted.

The published image captures the installed toolchain without resolving those
repositories again on each Codespace launch. Startup only adjusts tool-cache
ownership when the runtime UID/GID differs from the image's `vscode` user.

To reproduce the image and run its preloaded examples without network access,
from the repository root:

```sh
docker build -t try-fstar -f .devcontainer/try-fstar/Dockerfile website
docker run --rm --network none try-fstar make check
```

For publishing replacement images and updating the pinned digest, see
[Maintaining the image](../../README.md#maintaining-the-image).
No hosted Codespace is created by these commands.
