# TryFStar

Try F*, Pulse, PAL, and PAL-CSharp in a working browser-based environment.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/FStarLang/TryFStar?quickstart=1&devcontainer_path=.devcontainer%2Ftry-fstar%2Fdevcontainer.json)

Choose **Try F*: Pulse, PAL, and PAL-CSharp** if prompted. The configuration
requests at least 4 cores, 8 GB RAM, and 32 GB disk. Your first launch builds
the toolchains and translators, which takes several minutes; it is not an
instant-start image. GitHub Codespaces usage is subject to your account's
quota and billing settings.

The browser opens VS Code in `website/playground/`, with:

- A pinned binary F*/Pulse release and the F* editor assistant.
- PAL and PAL-CSharp, with prebuilt support libraries.
- Editable examples for functional F*, Pulse, annotated C, and annotated C#.
- Extraction to C, OCaml, and F#, with native compilation and execution.
- F* and Pulse tutorial sources, exercises, solutions, and the static book.

Setup checks the examples automatically and preserves existing edits.
In the terminal:

```sh
make check                   # Verify, extract, compile, and run all samples
make -C functional check     # F*: list append to C, OCaml, and F#
make -C pulse check          # Pulse: multiplication to C, OCaml, and F#
make -C pal check            # Translate and verify annotated C; run the C
make -C pal-csharp check     # Prove C# insertion sort; run the C#
make serve                   # Open forwarded port 8000 for the tutorial
```

Copied editable sources initially appear as untracked files. Commit the
sources and solutions you want to retain before deleting a Codespace.
Tutorial exercises intentionally include holes and expected errors.

For local use, clone this repository in VS Code and select
**Dev Containers: Reopen in Container**. Docker is required; the image targets
Linux x86-64.

See [the playground guide](website/playground/README.md) for precise
guarantees, pinned versions, tutorial compatibility notes, and Docker commands.
The [F* website](https://fstar-lang.org/) provides the broader introduction.

## License

This repository uses the Apache License 2.0. Bundled PAL and PAL-CSharp
example files retain their separate notices; see [NOTICE](NOTICE).
