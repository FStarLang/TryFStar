"""Serve the bundled tutorial, optionally as a container-lifetime background service."""
import argparse
from contextlib import closing
from functools import partial
import hashlib
from http.client import HTTPConnection
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit


def root_id(directory):
    return hashlib.sha256(os.fsencode(Path(directory).resolve())).hexdigest()


class TutorialHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("X-TryFStar-Root", root_id(self.directory))
        super().end_headers()

    def send_head(self):
        path = urlsplit(self.path).path
        if path in ("/", "/index.html", "/tutorial/book"):
            self.send_response(302)
            self.send_header("Location", "/tutorial/book/")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None
        if not path.startswith("/tutorial/book/"):
            self.send_error(404)
            return None
        candidate = Path(self.translate_path(self.path)).resolve()
        root = Path(self.directory).resolve()
        paths = [candidate]
        if candidate.is_dir():
            paths.extend(candidate / name for name in ("index.html", "index.htm"))
        if any(not item.resolve().is_relative_to(root) for item in paths):
            self.send_error(404)
            return None
        return super().send_head()

    def translate_path(self, path):
        return super().translate_path(path.removeprefix("/tutorial/book/"))

    def list_directory(self, path):
        self.send_error(404)
        return None


def configure_codespaces_port(port):
    if os.environ.get("CODESPACES") == "true":
        subprocess.run(
            ["gh", "codespace", "ports", "visibility", f"{port}:public",
             "--codespace", os.environ["CODESPACE_NAME"]],
            check=True, timeout=30,
        )


def serve(directory, port):
    handler = partial(TutorialHandler, directory=directory)
    with ThreadingHTTPServer(("0.0.0.0", port), handler, bind_and_activate=False) as server:
        server.server_bind()
        # Reserve the docs-only socket before publishing, but do not trigger preview discovery yet.
        configure_codespaces_port(server.server_port)
        server.server_activate()
        print(f"Tutorial at http://localhost:{server.server_port}/tutorial/book/", flush=True)
        server.serve_forever()


def is_running(directory, port):
    try:
        with closing(HTTPConnection("127.0.0.1", port, timeout=2)) as connection:
            connection.request("HEAD", "/tutorial/book/index.html")
            response = connection.getresponse()
            if response.status == 200 and response.getheader("X-TryFStar-Root") == root_id(directory):
                return True
    except ConnectionRefusedError:
        return False
    raise RuntimeError(f"Port {port} is occupied by another server; stop it before starting the tutorial.")


def start_background(directory, port):
    if is_running(directory, port):
        configure_codespaces_port(port)
        print(f"Tutorial already running on port {port}.")
        return None
    with tempfile.NamedTemporaryFile(prefix="tryfstar-tutorial-", suffix=".log", delete=False) as log:
        log_path = Path(log.name)
        process = subprocess.Popen(
            [sys.executable, "-u", str(Path(__file__).resolve()),
             "--directory", str(Path(directory).parent.parent), "--port", str(port)],
            stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    ready = False
    try:
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"Tutorial server failed:\n{log_path.read_text()}")
            if is_running(directory, port):
                ready = True
                print(f"Tutorial ready on port {port}. Log: {log_path}")
                return process
            time.sleep(0.1)
        raise TimeoutError(f"Tutorial did not start within 45 seconds. See {log_path}.")
    finally:
        if not ready and process.poll() is None:
            process.terminate()
            process.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--background", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    website = args.directory.resolve()
    directory = website / "tutorial/book"
    if directory.resolve() != directory:
        raise ValueError("The bundled tutorial directory must not be a symbolic link.")
    if not (directory / "index.html").is_file():
        raise FileNotFoundError(f"Bundled tutorial is missing from {directory / 'index.html'}")
    if args.background:
        start_background(directory, args.port)
    elif is_running(directory, args.port):
        configure_codespaces_port(args.port)
        print(f"Tutorial already running on port {args.port}; preview it from the Ports panel.")
    else:
        serve(directory, args.port)


if __name__ == "__main__":
    main()
