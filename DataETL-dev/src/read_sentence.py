import numpy as np
import pandas as pd
from tqdm import tqdm

class sentence:

    def __init__(self, input_segment):
        self.id = input_segment[0]
        self.rank = input_segment[1]
        self.cui1 = input_segment[2]
        self.cui1_type = input_segment[3]
        self.cui2 = input_segment[4]
        self.cui2_type = input_segment[5]
        # 注意非空白分隔符
        self.text = input_segment[6].replace(u'\xa0', u' ').replace(u'\u200a', u' ').replace(u'\u2009', u' ')
        self.article_structure = input_segment[7]
        self.pos1 = eval(input_segment[8])
        self.pos2 = eval(input_segment[9])
        self.word_count = input_segment[10]
        self.is_title1 = input_segment[11]
        self.is_title2 = input_segment[12]
        self.cui1_pos = self.pos1[0]
        self.cui2_pos = self.pos2[0]

    def __str__(self):
        return self.id + '|' + self.rank + '|' + self.cui1 + '|' + self.cui1_type + '|' + self.cui2 + '|' \
                + self.cui2_type + '|' + self.text + '|' + self.article_structure + '|' + str(self.pos1) + '|' \
                + str(self.pos2) + '|' + str(self.word_count) + '|' + self.is_title1 + '|' + self.is_title2 + '\n'   
    
    def get_eps(self):
        return self.cui1 + '|' + self.cui2

    def get_masks(self):
        text_segment = self.text.split()
        return text_segment[self.cui1_pos] + '|' + text_segment[self.cui2_pos]


def generate_new_eps(cui_type_df1, cui_type_df2, old_eps_list): 
    cuis_info = []
    for old_eps in tqdm(old_eps_list):
        old_cui1, old_cui2 = old_eps.split('|')[0], old_eps.split('|')[1]
        mask1 = cui_type_df1[cui_type_df1['cui']==old_cui1].iloc[0, 1]
        mask2 = cui_type_df2[cui_type_df2['cui']==old_cui2].iloc[0, 1]
        cui1_candidates = cui_type_df1[cui_type_df1['mask']==mask1].reset_index(drop=True)
        cui2_candidates = cui_type_df2[cui_type_df2['mask']==mask2].reset_index(drop=True)
        cui1, cui2 = cui1_candidates.sample(1).iloc[0, [0,1,2]], cui2_candidates.sample(1).iloc[0, [0,1,2]]
        cui_eps = cui1[0] + '|' + cui2[0]
        cui_mask = cui1[1] + '|' + cui2[1]
        cui_types = cui1[2] + '|' + cui2[2]
        cui_info = (cui_eps, cui_mask, cui_types)
        cuis_info.append(cui_info)
    return cuis_info


def generate_typed_cui(cuis, semgroup, type_):
    type_idx = pd.DataFrame(columns=["mask", "type"])
    for id,row in semgroup.iterrows():
        if row[1]==type_:
            type_idx.loc[id] =[row[2].lower(), row[3]]
    typed_cui = cuis.merge(type_idx, left_on='sty', right_on='type')[["cui", "mask", "type"]]
    return typed_cui
