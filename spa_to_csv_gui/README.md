# SPA to CSV converter

# Just download the folder and double click on either the Mac or Windows app



Combines every `.SPA` file in a folder (OMNIC/Thermo FTIR spectra) into a single CSV:
the first column is `Wavenumber` and each following column is one spectrum,
named after its file.

## Installation

You need Python 3.9 or newer. Install the dependencies once:

```
pip install -r requirements.txt
```

(or `conda install -c spectrocat spectrochempy` if you use conda)

## Starting it with a double-click (macOS)

Double-click **SPA to CSV - Mac.app** in this folder. It finds a Python installation with
the required packages (Anaconda, Miniconda, Homebrew, ...) and opens the window,
without a Terminal. To put it on the Dock or Desktop, make an alias
(⌘+⌥ drag) rather than moving the app: it has to stay next to these scripts.
If nothing appears, the log is in `~/Library/Logs/SPA to CSV.log`.

On another Mac, the first time macOS may say the app is from an unidentified
developer: right-click it → **Open** → **Open**.

## Starting it with a double-click (Windows)

Double-click **SPA to CSV - Windows.bat** in this folder. It finds a Python installation with
the required packages (Anaconda, Miniconda, the python.org `py` launcher, or
Python on the PATH) and opens the window. A console flashes briefly and closes.
For a Desktop shortcut: right-click the file → **Send to** → **Desktop (create
shortcut)**; keep the `.bat` itself next to these scripts.
If nothing appears, the log is in `%LOCALAPPDATA%\SPA to CSV.log`. If no suitable
Python is found, the console stays open and says so.

The first time, Windows SmartScreen may warn about a file from the internet:
**More info** → **Run anyway**.

## Usage with the window (recommended)

```
python run_gui.py
```

1. **Browse...** to select the folder that contains the `.SPA` files.
2. Choose where to save the CSV. A default name is suggested automatically.
3. Leave **Wavenumbers → Read from the .SPA files** selected. The wavenumber
   axis (number of points, start and end) is read from the files themselves.
   Use **Manual range** only if you need an evenly spaced axis between two values.
4. Click **Convert**. Progress and any errors are shown in the log.

## Usage from the terminal

```
python run_cli.py /path/to/spa_folder
python run_cli.py /path/to/spa_folder -o /path/to/output.csv
python run_cli.py /path/to/spa_folder --range 4000.188 649.90
```

## Files

| File            | What it does                                          |
|-----------------|-------------------------------------------------------|
| `run_gui.py`    | Starts the window                                     |
| `run_cli.py`    | Command-line version                                  |
| `gui.py`        | The Tkinter window                                    |
| `converter.py`  | Finds the files, reads them in parallel, merges, saves |
| `spa_reader.py` | Reads one `.SPA` file and its wavenumber axis         |
