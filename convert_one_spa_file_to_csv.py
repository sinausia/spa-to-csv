import spectrochempy as scp
import pandas as pd
import numpy as np

spa_file_path = r'/Users/danielsinausia/Downloads/DS_00145_01.SPA'
csv_file_path = r'/Users/danielsinausia/Downloads/DS_00145_01.csv'

dataset = scp.read(spa_file_path)
data = dataset.data.T
df = pd.DataFrame(data, columns=dataset.x_labels)

wavenumbers = np.linspace(4000.1885, 649.9040, 6950)
df.insert(0, 'Wavenumber', wavenumbers)

df.to_csv(csv_file_path, index=False, header=False)
