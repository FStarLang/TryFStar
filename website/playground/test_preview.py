from functools import partial
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch

from preview import is_running, start_background, TutorialHandler


class PreviewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="tryfstar-preview-")
        self.addCleanup(temporary.cleanup)
        self.website = Path(temporary.name)
        book = self.website / "tutorial/book"
        (book / "static").mkdir(parents=True)
        (book / "index.html").write_text('<a href="chapter.html">Read</a>')
        (book / "chapter.html").write_text("<h1>A chapter</h1>")
        (book / "static/theme.css").write_text("body { color: black; }")
        logging = patch.object(TutorialHandler, "log_message")
        logging.start()
        self.addCleanup(logging.stop)
        server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(TutorialHandler, directory=self.website),
        )
        self.addCleanup(server.server_close)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join)
        self.addCleanup(server.shutdown)
        self.port = server.server_port

    def request(self, method, path):
        with closing(HTTPConnection("127.0.0.1", self.port, timeout=2)) as connection:
            connection.request(method, path)
            response = connection.getresponse()
            return response.status, response.getheader("Location"), response.read()

    def test_preview_opens_the_book_and_serves_chapters_and_assets(self):
        for path in ("/", "/index.html"):
            for method in ("GET", "HEAD"):
                self.assertEqual(self.request(method, path), (302, "/tutorial/book/", b""))
        for path, content in (
            ("/tutorial/book/", b'<a href="chapter.html">Read</a>'),
            ("/tutorial/book/chapter.html", b"<h1>A chapter</h1>"),
            ("/tutorial/book/static/theme.css", b"body { color: black; }"),
        ):
            status, _, body = self.request("GET", path)
            self.assertEqual(status, 200)
            self.assertEqual(body, content)

    def test_reuses_its_server_but_rejects_another_checkout(self):
        self.assertTrue(is_running(self.website, self.port))
        self.assertIsNone(start_background(self.website, self.port))
        with self.assertRaisesRegex(RuntimeError, "occupied by another server"):
            start_background(self.website / "another-checkout", self.port)

    def test_missing_book_is_reported_without_starting_a_server(self):
        result = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("preview.py")),
             "--background", "--directory", str(self.website / "missing")],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Bundled tutorial is missing", result.stderr)


if __name__ == "__main__":
    unittest.main()
from contextlib import closing
