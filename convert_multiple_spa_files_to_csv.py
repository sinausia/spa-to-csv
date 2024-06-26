import spectrochempy as scp
import pandas as pd
import numpy as np
import glob
import os


folder_path = r'The directory where your spa files are stored'
final_csv_path = r'"the directory of the folder where you want your csv file to be created\final_result.csv'


spa_files = glob.glob(os.path.join(folder_path, '*.SPA'))

dataframes = []
for spa_file_path in spa_files:
    dataset = scp.read(spa_file_path)
    data = dataset.data.T
    df = pd.DataFrame(data, columns=dataset.x_labels)
    wavenumbers = np.linspace(4000.1885, 649.9040, 6950)
    df.insert(0, 'Wavenumber', wavenumbers)
    dataframes.append(df)


final_df = dataframes[0]  # Initialize with the first dataframe
for df in dataframes[1:]:
    final_df = pd.merge(final_df, df[['Wavenumber', df.columns[1]]], on='Wavenumber', how='outer')

column_names = ['Wavenumber'] + [os.path.splitext(os.path.basename(file_path))[0] for file_path in spa_files]
final_df.columns = column_names


final_df.to_csv(final_csv_path, index=False)
