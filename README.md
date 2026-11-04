# TryFStar

Try F*, Pulse, PAL, and PAL-CSharp in a working browser-based environment.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/FStarLang/TryFStar?quickstart=1&devcontainer_path=.devcontainer%2Ftry-fstar%2Fdevcontainer.json)

Choose **Try F*: Pulse, PAL, and PAL-CSharp** if prompted. The configuration
requests at least 4 cores, 8 GB RAM, and 32 GB disk. It downloads a prebuilt,
digest-pinned image instead of compiling the toolchains and translators.
The first image download is substantial; subsequent starts reuse it.
GitHub Codespaces usage is subject to your account's quota and billing settings.

The browser opens VS Code in `website/playground/`, with:

- A pinned binary F*/Pulse release and the F* editor assistant.
- PAL and PAL-CSharp, with prebuilt support libraries.
- Editable examples for functional F*, Pulse, annotated C, and annotated C#.
- Extraction to C, OCaml, and F#, with native compilation and execution.
- F* and Pulse tutorial sources, exercises, solutions, and the static book.

The tutorial server starts automatically, and port **8000** opens the rendered
book in an editor preview beside your code. Edit the matching files under
`tutorials/`, such as `Part1.GettingOffTheGround.fst` or
`pulse/PulseTutorial.Intro.fst`. If you close the preview, right-click port
**8000** in the **Ports** panel and choose **Preview in Editor**.

The image's examples are verified during its build. Startup copies editable
sources, checks tool availability, and preserves existing edits; it does not
repeat the full verification and compilation matrix.
In the terminal:

```sh
make check                   # Verify, extract, compile, and run all samples
make -C functional check     # F*: list append to C, OCaml, and F#
make -C pulse check          # Pulse: multiplication to C, OCaml, and F#
make -C pal check            # Translate and verify annotated C; run the C
make -C pal-csharp check     # Prove C# insertion sort; run the C#
make serve                   # Start the tutorial manually if needed
```

Copied editable sources initially appear as untracked files. Commit the
sources and solutions you want to retain before deleting a Codespace.
Tutorial exercises intentionally include holes and expected errors.
Existing Codespaces need the latest `main` and **Codespaces: Rebuild Container**
to pick up the automatic preview configuration; the prebuilt image is unchanged.

For local use, clone this repository in VS Code and select
**Dev Containers: Reopen in Container**. Docker is required; the image targets
Linux x86-64.

See [the playground guide](website/playground/README.md) for precise
guarantees, pinned versions, tutorial compatibility notes, and Docker commands.
The [F* website](https://fstar-lang.org/) provides the broader introduction.

## Maintaining the image

[Publish playground image](https://github.com/FStarLang/TryFStar/actions/workflows/container.yml)
rebuilds and checks the image when toolchain inputs change, or on manual dispatch.
Normal rebuilds use a GitHub Actions layer cache and publish to
`ghcr.io/fstarlang/tryfstar`.

After a successful build, copy the immutable reference from the run summary
into `.devcontainer/try-fstar/devcontainer.json`. Verify an anonymous
`docker pull` succeeds before committing the new pin. For the first publication,
the package may need to be made public in its GitHub package settings.
Moving the `latest` tag does not change existing Codespaces or this pinned setup.

## License

This repository uses the Apache License 2.0. Bundled PAL and PAL-CSharp
example files retain their separate notices; see [NOTICE](NOTICE).
