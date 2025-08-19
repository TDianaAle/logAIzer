import pandas as pd

unsw_files = [
    'data/reduced/UNSW-NB15_1.csv',
    'data/reduced/UNSW-NB15_2.csv',
    'data/reduced/UNSW-NB15_3.csv',
    'data/reduced/UNSW-NB15_4.csv'
]
gt_file = 'data/reduced/UNSW-NB15_GT.csv'

df_unsw = pd.read_csv(unsw_files[0], low_memory=False)
df_gt = pd.read_csv(gt_file, low_memory=False)

print("Colonne UNSW-NB15:", df_unsw.columns.tolist())
print("Colonne GT:", df_gt.columns.tolist())
