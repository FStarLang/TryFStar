from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


@unittest.skipUnless(
    all(shutil.which(tool) for tool in ("dotnet", "palcs", "fstar.exe", "make")),
    "requires the playground verification toolchain",
)
class PalCSharpEditorTests(unittest.TestCase):
    def test_failed_proof_reaches_the_csharp_analyzer_and_clears_after_repair(self):
        with tempfile.TemporaryDirectory(prefix="try-fstar-palcs-") as directory:
            workspace = Path(directory)
            subprocess.run(
                [sys.executable, str(HERE / "setup.py"), str(workspace)],
                check=True, stdout=subprocess.DEVNULL,
            )
            project = workspace / "pal-csharp"

            def run(*command):
                return subprocess.run(
                    command, cwd=project, text=True,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180,
                )

            build = ("dotnet", "build", "Pal.Editor.csproj", "--no-restore", "--verbosity", "quiet")
            result = run("make", "-s", "editor-setup")
            self.assertEqual(result.returncode, 0, result.stdout)
            report = project / "_build/pulse/verification.txt"
            self.assertIn("Not yet verified", report.read_text())
            result = run(*build)
            self.assertEqual(result.returncode, 0, result.stdout)

            source = project / "InsertionSortSorted.cs"
            original = source.read_text()
            invalid = original.replace("a[j + 1] = key;", "a[j + 1] = 0;")
            self.assertNotEqual(original, invalid)
            source.write_text(invalid)
            result = run("make", "-s", "verify")
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("InsertionSortSorted.cs(", result.stdout)
            self.assertIn("PALCS0600\tInsertionSortSorted.cs\t", report.read_text())

            result = run(*build)
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("error PALCS0600", result.stdout)
            self.assertNotIn("AD0001", result.stdout)

            source.write_text(original)
            result = run("make", "-s", "verify")
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertNotIn("PALCS0600", report.read_text())
            result = run(*build)
            self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
