"""Start the SPA to CSV converter window.

Usage:
    python run_gui.py
"""
import multiprocessing

from gui import main

if __name__ == '__main__':
    # Needed so the parallel workers start correctly on Windows/macOS
    multiprocessing.freeze_support()
    main()
