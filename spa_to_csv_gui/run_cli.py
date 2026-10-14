"""Command-line version of the converter (no window).

Usage:
    python run_cli.py /path/to/spa_folder
    python run_cli.py /path/to/spa_folder -o /path/to/output.csv
    python run_cli.py /path/to/spa_folder --range 4000.188 649.90
"""
import argparse
import os

from converter import convert_folder


def main():
    parser = argparse.ArgumentParser(description="Combine all .SPA files in a folder into one CSV.")
    parser.add_argument('folder', help="Folder containing the .SPA files")
    parser.add_argument('-o', '--output', help="Output CSV path (default: <folder>/<folder name>.csv)")
    parser.add_argument('--range', nargs=2, type=float, metavar=('START', 'END'),
                        help="Use an evenly spaced wavenumber axis instead of the one stored in the files")
    parser.add_argument('--workers', type=int, default=None, help="Number of parallel workers")
    args = parser.parse_args()

    folder = os.path.abspath(args.folder)
    output = args.output or os.path.join(folder, os.path.basename(folder) + '.csv')
    convert_folder(folder, output, manual_range=tuple(args.range) if args.range else None,
                   max_workers=args.workers)


if __name__ == '__main__':
    main()
