import pandas as pd
import numpy as np


cui_list = pd.read_csv("../data/A0002SemGroups.txt", sep='|', header=None)
cui_mask_dict = {}
for id, row in cui_list.iterrows():
    cui_mask_dict[row[3]] = row[2].lower()
diso_list = (np.array(cui_list[61:73][[3]]).reshape(1, -1).tolist())[0]

with open("../data/general_clean_neg_all.txt", 'r') as in_file, open("../data/candidate_neg_diso.txt", 'w') as out_file:
    while True:
        line = in_file.readline()
        if not line:
            break
        parts = line.split('|')
        cui1_type = parts[3]
        if cui1_type in diso_list:
            out_file.write(line)
