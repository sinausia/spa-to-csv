"""Start the SPA to CSV converter window.

Usage:
    python run_gui.py
"""
import multiprocessing
import os
import sys

from gui import main


def log_to_file_if_no_console(name):
    """pythonw (Windows double-click) has no console, so keep errors in a log file."""
    if sys.stdout is not None and sys.stderr is not None:
        return
    folder = os.environ.get('LOCALAPPDATA') or os.path.expanduser('~')
    sys.stdout = sys.stderr = open(os.path.join(folder, f'{name}.log'), 'w', buffering=1)


if __name__ == '__main__':
    # Needed so the parallel workers start correctly on Windows/macOS
    multiprocessing.freeze_support()
    log_to_file_if_no_console('SPA to CSV')
    main()
