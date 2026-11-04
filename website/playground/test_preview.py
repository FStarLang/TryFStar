from functools import partial
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
import os
import socket
import subprocess
import sys
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch

from preview import is_running, serve, start_background, TutorialHandler


class PreviewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="tryfstar-preview-")
        self.addCleanup(temporary.cleanup)
        self.website = Path(temporary.name)
        book = self.website / "tutorial/book"
        self.book = book
        (book / "static").mkdir(parents=True)
        (book / "index.html").write_text('<a href="chapter.html">Read</a>')
        (book / "chapter.html").write_text("<h1>A chapter</h1>")
        (book / "static/theme.css").write_text("body { color: black; }")
        logging = patch.object(TutorialHandler, "log_message")
        logging.start()
        self.addCleanup(logging.stop)
        server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(TutorialHandler, directory=book),
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
        self.assertTrue(is_running(self.book, self.port))
        with patch("preview.configure_codespaces_port"):
            self.assertIsNone(start_background(self.book, self.port))
        with self.assertRaisesRegex(RuntimeError, "occupied by another server"):
            start_background(self.book / "another-checkout", self.port)

    def test_workspace_files_and_escaping_symlinks_are_not_served(self):
        private = self.website / "playground/Learner.fst"
        private.parent.mkdir()
        private.write_text("learner's unpublished edits")
        (self.book / "leak.fst").symlink_to(private)
        linked_index = self.book / "linked-index"
        linked_index.mkdir()
        (linked_index / "index.html").symlink_to(private)
        for path in (
            "/playground/Learner.fst",
            "/tutorial/book/../../playground/Learner.fst",
            "/tutorial/book/%2e%2e/%2e%2e/playground/Learner.fst",
            "/tutorial/book/leak.fst",
            "/tutorial/book/linked-index/",
            "/tutorial/book/static/",
        ):
            status, _, body = self.request("GET", path)
            self.assertEqual(status, 404, path)
            self.assertNotIn(private.read_bytes(), body)

    def test_visibility_is_configured_before_the_reserved_socket_starts_listening(self):
        def publish(command, **kwargs):
            self.assertEqual(command[:4], ["gh", "codespace", "ports", "visibility"])
            self.assertEqual(command[5:], ["--codespace", "test-codespace"])
            self.assertTrue(kwargs["check"])
            port = int(command[4].split(":")[0])
            self.assertTrue(command[4].endswith(":public"))
            with socket.socket() as connection:
                self.assertNotEqual(connection.connect_ex(("127.0.0.1", port)), 0)

        def listen(server):
            self.assertEqual(server.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ACCEPTCONN), 1)

        with patch.dict(os.environ, {"CODESPACES": "true", "CODESPACE_NAME": "test-codespace"}):
            with patch("preview.subprocess.run", side_effect=publish) as command:
                with patch.object(ThreadingHTTPServer, "serve_forever", autospec=True, side_effect=listen):
                    serve(self.book, 0)
                command.assert_called_once()

    def test_visibility_errors_prevent_the_public_server_from_starting(self):
        failure = subprocess.CalledProcessError(1, ["gh"])
        with patch.dict(os.environ, {"CODESPACES": "true", "CODESPACE_NAME": "test-codespace"}):
            with patch("preview.subprocess.run", side_effect=failure):
                with patch.object(ThreadingHTTPServer, "serve_forever") as loop:
                    with self.assertRaises(subprocess.CalledProcessError):
                        serve(self.book, 0)
                    loop.assert_not_called()

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
