#!/usr/bin/env python3
"""Seed editable examples without overwriting a learner's existing files."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
PROJECTS = {
    "functional": ("functional", ["ListAppend.fst", "test.c", "test.ml", "test.fsx"]),
    "pulse": ("pulse", ["Multiply.fst", "test.c", "test.ml"]),
    "pal": ("pal", ["multiply.c", "pal.h", "test.c", "LICENSE.pal"]),
    "pal-csharp": ("pal-cs", ["InsertionSortSorted.cs", "Test.cs", "LICENSE"]),
}


def copy_new(source, destination):
    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path, nargs="?", default=HERE)
    workspace = parser.parse_args().workspace.resolve()
    website = HERE.parent
    examples = website / "examples"
    tutorials = website / "tutorial/book/code"
    if not examples.is_dir():
        examples = Path("/opt/playground-seed/examples")
        tutorials = Path("/opt/playground-seed/tutorials")
    if not tutorials.is_dir():
        raise FileNotFoundError(f"Tutorial source directory is missing: {tutorials}")
    for name in ("Makefile", "setup.py", "test_setup.py", "preview.py", "test_preview.py", "README.md"):
        copy_new(HERE / name, workspace / name)
    copy_new(HERE / ".vscode/tasks.json", workspace / ".vscode/tasks.json")
    copy_new(HERE / "tutorial-compat/pulse-intro.patch",
             workspace / "tutorial-compat/pulse-intro.patch")
    for project, (original, files) in PROJECTS.items():
        destination = workspace / project
        copy_new(HERE / project / "Makefile", destination / "Makefile")
        if project in ("functional", "pulse"):
            copy_new(HERE / project / "test.fsx", destination / "test.fsx")
        for file in files:
            copy_new(examples / original / file, destination / file)
        includes = []
        if project == "pal":
            includes.append(str(Path(os.environ.get("PAL_ROOT", "/opt/pal")) / "pulse"))
            pal_config = destination / "pal.config.json"
            if not pal_config.exists():
                pal_config.write_text(json.dumps({
                    "files": "multiply.c",
                    "options": ["--outdir", "_build/pulse"],
                }, indent=2) + "\n")
        if project == "pal-csharp":
            includes.append(str(Path(os.environ.get("PAL_CS_ROOT", "/opt/pal-csharp")) / "pulse"))
            copy_new(HERE / project / "Sort.csproj", destination / "Sort.csproj")
            copy_new(HERE / project / "Directory.Build.props", destination / "Directory.Build.props")
        if includes:
            includes += [str(Path(include) / "_cache") for include in includes]
            translated = destination / "_build/pulse"
            translated.mkdir(parents=True, exist_ok=True)
            includes.append(str(translated))
        (destination / "_build/cache").mkdir(parents=True, exist_ok=True)
        options = ["--cache_checked_modules", "--cache_dir", str(destination / "_build/cache")]
        configuration = {
            "fstar_exe": os.environ.get("FSTAR_EXE", "fstar.exe"),
            "options": options,
            "include_dirs": includes,
        }
        config = destination / ".fst.config.json"
        if not config.exists():
            config.write_text(json.dumps(configuration, indent=2) + "\n")
    for source in tutorials.rglob("*"):
        if source.is_file():
            destination = workspace / "tutorials" / source.relative_to(tutorials)
            if copy_new(source, destination) and source.name == "PulseTutorial.Intro.fst":
                subprocess.run([
                    "patch", "--batch", "--fuzz=0", str(destination),
                    str(HERE / "tutorial-compat/pulse-intro.patch"),
                ], check=True)
    tutorial_directory = workspace / "tutorials"
    (tutorial_directory / "_build/cache").mkdir(parents=True, exist_ok=True)
    config = tutorial_directory / ".fst.config.json"
    if not config.exists():
        config.write_text(json.dumps({
            "fstar_exe": os.environ.get("FSTAR_EXE", "fstar.exe"),
            "options": [
                "--cache_checked_modules", "--cache_dir",
                str(tutorial_directory / "_build/cache"),
            ],
            "include_dirs": [str(tutorial_directory), str(tutorial_directory / "pulse")],
        }, indent=2) + "\n")
    print(f"Examples and tutorial files ready in {workspace}")


if __name__ == "__main__":
    main()
