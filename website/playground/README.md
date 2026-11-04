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
or translators. Subsequent starts reuse the image. Its immutable registry
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
To read the tutorial, run `make serve`, open forwarded port **8000**,
and visit `/tutorial/book/`. This serves the static book, not the legacy
PHP-backed web verifier. Source verification happens in the editor or terminal.

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
