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
        if urlsplit(self.path).path in ("/", "/index.html"):
            self.send_response(302)
            self.send_header("Location", "/tutorial/book/")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None
        return super().send_head()


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
        print(f"Tutorial already running on port {port}.")
        return None
    with tempfile.NamedTemporaryFile(prefix="tryfstar-tutorial-", suffix=".log", delete=False) as log:
        log_path = Path(log.name)
        process = subprocess.Popen(
            [sys.executable, "-u", str(Path(__file__).resolve()),
             "--directory", str(directory), "--port", str(port)],
            stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    ready = False
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"Tutorial server failed:\n{log_path.read_text()}")
            if is_running(directory, port):
                ready = True
                print(f"Tutorial ready on port {port}. Log: {log_path}")
                return process
            time.sleep(0.1)
        raise TimeoutError(f"Tutorial did not start within 10 seconds. See {log_path}.")
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
    directory = args.directory.resolve()
    if not (directory / "tutorial/book/index.html").is_file():
        raise FileNotFoundError(f"Bundled tutorial is missing from {directory / 'tutorial/book/index.html'}")
    if args.background:
        start_background(directory, args.port)
    elif is_running(directory, args.port):
        print(f"Tutorial already running on port {args.port}; preview it from the Ports panel.")
    else:
        handler = partial(TutorialHandler, directory=directory)
        with ThreadingHTTPServer(("0.0.0.0", args.port), handler) as server:
            print(f"Tutorial at http://localhost:{args.port}/tutorial/book/", flush=True)
            server.serve_forever()


if __name__ == "__main__":
    main()
