import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="try-fstar-setup-")
        self.addCleanup(self.temporary.cleanup)
        self.workspace = Path(self.temporary.name)

    def setup_workspace(self):
        subprocess.run(
            [sys.executable, str(HERE / "setup.py"), str(self.workspace)],
            check=True,
            stdout=subprocess.DEVNULL,
        )

    def test_seeds_projects_tutorials_and_editor_configuration(self):
        self.setup_workspace()
        for project, source in (
            ("functional", "ListAppend.fst"),
            ("pulse", "Multiply.fst"),
            ("pal", "multiply.c"),
            ("pal-csharp", "InsertionSortSorted.cs"),
        ):
            directory = self.workspace / project
            self.assertTrue((directory / source).is_file())
            self.assertTrue((directory / "Makefile").is_file())
            config = json.loads((directory / ".fst.config.json").read_text())
            self.assertIn("--cache_checked_modules", config["options"])
        pal_config = json.loads((self.workspace / "pal/pal.config.json").read_text())
        self.assertEqual(pal_config["files"], "multiply.c")
        self.assertEqual(pal_config["options"], ["--outdir", "_build/pulse"])
        pal_fstar = json.loads((self.workspace / "pal/.fst.config.json").read_text())
        self.assertIn(str(self.workspace / "pal/_build/pulse"), pal_fstar["include_dirs"])
        self.assertTrue((self.workspace / "tutorials/Part1.GettingOffTheGround.fst").is_file())
        self.assertTrue((self.workspace / "tutorials/pulse/PulseTutorial.Intro.fst").is_file())
        self.assertTrue((self.workspace / ".vscode/tasks.json").is_file())

    def test_repeated_setup_preserves_edits_and_restores_missing_sources(self):
        self.setup_workspace()
        source = self.workspace / "functional/ListAppend.fst"
        config = self.workspace / "functional/.fst.config.json"
        source.write_text("learner's source edits\n")
        config.write_text('{"options":["--fuel","2"]}\n')
        pal_config = self.workspace / "pal/pal.config.json"
        custom_pal = {"files": ["other.c"], "options": ["--outdir", "_build/custom"]}
        pal_config.write_text(json.dumps(custom_pal))
        missing = self.workspace / "pal/multiply.c"
        missing.unlink()
        self.setup_workspace()
        self.assertEqual(source.read_text(), "learner's source edits\n")
        self.assertEqual(json.loads(config.read_text())["options"], ["--fuel", "2"])
        self.assertEqual(json.loads(pal_config.read_text()), custom_pal)
        self.assertTrue(missing.is_file())


if __name__ == "__main__":
    unittest.main()
