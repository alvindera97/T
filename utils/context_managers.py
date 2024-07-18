"""
Utilities context manager module

This module contains code for utils (utilities) which are [or related to] context managers.

Classes:
  CaptureTerminalOutput
"""
import io
import sys


class CaptureTerminalOutput:
    """Context manager for capturing content on terminal"""
    def __enter__(self):
        self._stdout = sys.stdout
        self._stringio = io.StringIO()
        sys.stdout = self._stringio

        return self._stringio

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._stdout
        self._stringio.close()
