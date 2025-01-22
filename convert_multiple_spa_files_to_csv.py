import spectrochempy as scp
import pandas as pd
import numpy as np
import glob
import os

folder_path = r'directory of folder with SPA files'
final_csv_path = r'directory where to store your results/final_result.csv'

spa_files = sorted(glob.glob(os.path.join(folder_path, '*.SPA')) + glob.glob(os.path.join(folder_path, '*.spa')))
print(f"Found {len(spa_files)} .SPA files. Here are the first 5:\n{spa_files[:5]}")

dataframes = []
for spa_file_path in spa_files:
    try:
        print(f"Processing file: {spa_file_path}")
        dataset = scp.read(spa_file_path)
        data = dataset.data.T
        df = pd.DataFrame(data, columns=dataset.x_labels)
        wavenumbers = np.linspace(4000.188, 649.9040, 6950)  # To be changed, if necessary
        df.insert(0, 'Wavenumber', wavenumbers)
        dataframes.append(df)
    except Exception as e:
        print(f"Error processing {spa_file_path}: {e}")

if not dataframes:
    print("No dataframes were created. Check the .SPA files")
    exit()

print(f"Successfully processed {len(dataframes)} files.")

final_df = dataframes[0]
for i, df in enumerate(dataframes[1:], start=2):
    try:
        final_df = pd.merge(
            final_df,
            df[['Wavenumber', df.columns[1]]],
            on='Wavenumber',
            how='outer',
            suffixes=(None, f'_file{i}')
        )
    except Exception as e:
        print(f"Error merging file {i}: {e}")
column_names = ['Wavenumber'] + [os.path.splitext(os.path.basename(file_path))[0] for file_path in spa_files]
final_df.columns = column_names

# Save to CSV
final_df.to_csv(final_csv_path, index=False)
print(f"Final CSV saved at {final_csv_path}")
