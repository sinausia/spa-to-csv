"""Converting a whole folder of .SPA files into one combined CSV file.

This module has no GUI code, so it can also be used from other scripts:

    from converter import convert_folder
    convert_folder('/path/to/spa/folder', '/path/to/output.csv')
"""
import glob
import os
import shutil
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd

from spa_reader import process_spa_file


def find_spa_files(folder_path):
    """Return a sorted list of .SPA/.spa files in a folder (no duplicates)."""
    files = glob.glob(os.path.join(folder_path, '*.SPA')) + glob.glob(os.path.join(folder_path, '*.spa'))
    # On case-insensitive file systems (macOS) both patterns match the same files
    return sorted(set(files))


def _init_worker(config_root):
    """Give each worker process its own spectrochempy config folder.

    spectrochempy rewrites a JSON settings file on every read. When all workers
    share ~/.spectrochempy/config, one worker can read the file while another
    is writing it, which fails with errors like "Expecting value: line 1 column 1".
    """
    os.environ['SCP_CONFIG_HOME'] = tempfile.mkdtemp(dir=config_root)


def read_all(spa_files, manual_range=None, max_workers=None, log=print, progress=None, should_stop=None):
    """Read all files in parallel. Returns {path: DataFrame} for the files that succeeded."""
    results = {}
    total = len(spa_files)
    config_root = tempfile.mkdtemp(prefix='spa_to_csv_')
    try:
        with ProcessPoolExecutor(max_workers=max_workers or os.cpu_count(),
                                 initializer=_init_worker, initargs=(config_root,)) as executor:
            futures = [executor.submit(process_spa_file, f, manual_range) for f in spa_files]
            for i, future in enumerate(as_completed(futures), start=1):
                if should_stop and should_stop():
                    for f in futures:
                        f.cancel()
                    raise InterruptedError("Conversion cancelled")
                spa_file_path, df, error = future.result()
                if error:
                    log(f"Error processing {os.path.basename(spa_file_path)}: {error}")
                else:
                    results[spa_file_path] = df
                if progress:
                    progress(i, total)
                if i % 50 == 0 or i == total:
                    log(f"Processed {i}/{total} files")
    finally:
        shutil.rmtree(config_root, ignore_errors=True)
    return results


def merge_spectra(dataframes, names, log=print):
    """Combine spectra into one table: a 'Wavenumber' column plus one column per file."""
    reference = dataframes[0]['Wavenumber'].to_numpy()
    same_axis = all(
        len(df) == len(reference) and np.allclose(df['Wavenumber'].to_numpy(), reference)
        for df in dataframes
    )

    if same_axis:
        # Fast path: every file has the same wavenumber axis
        columns = {'Wavenumber': reference}
        for name, df in zip(names, dataframes):
            columns[name] = df.iloc[:, 1].to_numpy()
        return pd.DataFrame(columns)

    log("Warning: not all files share the same wavenumber axis. "
        "Merging on wavenumber; missing values will be left empty.")
    final_df = dataframes[0].rename(columns={dataframes[0].columns[1]: names[0]})
    for name, df in zip(names[1:], dataframes[1:]):
        final_df = pd.merge(
            final_df,
            df.rename(columns={df.columns[1]: name}),
            on='Wavenumber',
            how='outer',
        )
    return final_df.sort_values('Wavenumber', ascending=False).reset_index(drop=True)


def convert_folder(folder_path, output_csv, manual_range=None, max_workers=None,
                   log=print, progress=None, should_stop=None):
    """Read every .SPA file in ``folder_path`` and save them as one CSV.

    manual_range: None to use the wavenumbers stored in the files (recommended),
                  or (start, end) to build an evenly spaced axis instead.
    Returns the path of the saved CSV.
    """
    spa_files = find_spa_files(folder_path)
    if not spa_files:
        raise FileNotFoundError(f"No .SPA files found in {folder_path}")
    log(f"Found {len(spa_files)} .SPA files.")

    results = read_all(spa_files, manual_range, max_workers, log, progress, should_stop)

    # Preserve original sorted order, keeping only files that succeeded
    processed_files = [f for f in spa_files if f in results]
    if not processed_files:
        raise RuntimeError("No files could be read. Check the .SPA files.")

    log(f"Successfully processed {len(processed_files)} files. Merging them, hold a sec")
    first = results[processed_files[0]]['Wavenumber']
    log(f"Wavenumber axis detected: {len(first)} points, {first.iloc[0]:.3f} to {first.iloc[-1]:.3f} cm-1")

    names = [os.path.splitext(os.path.basename(fp))[0] for fp in processed_files]
    final_df = merge_spectra([results[f] for f in processed_files], names, log)

    os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)
    final_df.to_csv(output_csv, index=False)
    log(f"Final CSV saved at {output_csv}")
    return output_csv
