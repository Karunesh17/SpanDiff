import socket
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest


class LocalPlatformTests(unittest.TestCase):
    def test_installed_package_and_workspace_paths_with_spaces(self):
        import spandiff
        self.assertTrue(spandiff.__version__)
        with tempfile.TemporaryDirectory(prefix="SpanDiff path ") as directory:
            result = subprocess.run([sys.executable, "-c", "import pathlib; print(pathlib.Path.cwd().name)"],
                                    cwd=directory, check=True, capture_output=True, text=True)
            self.assertIn("SpanDiff path", result.stdout)

    def test_subprocess_cancellation_and_port_collision_are_observable(self):
        process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            process.terminate()
            process.wait(timeout=5)
            self.assertIsNotNone(process.returncode)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
        first = socket.socket()
        second = socket.socket()
        try:
            first.bind(("127.0.0.1", 0))
            port = first.getsockname()[1]
            with self.assertRaises(OSError):
                second.bind(("127.0.0.1", port))
        finally:
            first.close()
            second.close()


if __name__ == "__main__":
    unittest.main()
