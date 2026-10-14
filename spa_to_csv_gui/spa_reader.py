"""Reading a single .SPA file into a pandas DataFrame.

The wavenumber axis is taken from the file itself, so there is no need to
type in the number of points (e.g. 6950) or the start/end wavenumbers.
"""
import random
import time

import numpy as np
import pandas as pd


def get_wavenumbers(dataset, n_points, manual_range=None):
    """Return the wavenumber axis for a spectrochempy dataset.

    By default the axis stored in the .SPA file is used. If ``manual_range``
    is given as ``(start, end)``, an evenly spaced axis between those values
    is built instead, with the number of points detected from the data.
    """
    if manual_range is not None:
        start, end = manual_range
        return np.linspace(start, end, n_points)

    x = getattr(dataset, 'x', None)
    if x is not None and x.data is not None and len(x.data) == n_points:
        return np.asarray(x.data, dtype=float)

    raise ValueError(
        "The file does not contain a usable wavenumber axis. "
        "Use the 'manual range' option and enter the start/end wavenumbers."
    )


def process_spa_file(spa_file_path, manual_range=None, max_attempts=5):
    """Read one .SPA file. Returns (path, DataFrame or None, error or None).

    The DataFrame has two columns: 'Wavenumber' and the absorbance values.
    """
    import spectrochempy as scp

    last_error = None
    for attempt in range(max_attempts):
        try:
            dataset = scp.read(spa_file_path)
            data = np.asarray(dataset.data).T
            if data.ndim == 1:
                data = data.reshape(-1, 1)
            df = pd.DataFrame(data[:, :1], columns=['Absorbance'])
            df.insert(0, 'Wavenumber', get_wavenumbers(dataset, len(df), manual_range))
            return spa_file_path, df, None
        except ValueError as e:
            # Not a transient problem, retrying won't help
            return spa_file_path, None, str(e)
        except Exception as e:
            # spectrochempy writes a shared JSON config/cache file on every read,
            # so parallel workers occasionally race and read it mid-write.
            # A short retry almost always clears the race.
            last_error = str(e)
            time.sleep(0.05 + random.random() * 0.2)
    return spa_file_path, None, last_error
