import spectrochempy as scp
import pandas as pd
import numpy as np

spa_file_path = r'"The directory of your spa file"'
csv_file_path = r'"The directory of your spa file"\"the name of your csv file".csv'

dataset = scp.read(spa_file_path)
data = dataset.data.T
df = pd.DataFrame(data, columns=dataset.x_labels)

wavenumbers = np.linspace((4000.1885, 649.9040, 6950))
df.insert(0, 'Wavenumber', wavenumbers)

df.to_csv(csv_file_path, index=False, header=False)
