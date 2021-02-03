import argparse
import pandas as pd
import numpy as np
from tqdm import tqdm
from parameters import parameters
from read_sentence import *


class sentence_neg1(sentence):
    def __init__(self, input_segment):
        super().__init__(input_segment)

    def process(self, sub_text, cui_info):
        text_segment = self.text.split()
        (cui_eps, cui_masks, cui_types) = cui_info
        text_segment = text_segment[0: min(self.cui1_pos, self.cui2_pos)+1] + sub_text.split() + text_segment[max(self.cui1_pos, self.cui2_pos):]
    
        if self.cui1_pos < self.cui2_pos:
            self.cui2_pos = self.cui1_pos + len(sub_text.split()) + 1
        else:
            self.cui1_pos = self.cui2_pos + len(sub_text.split()) + 1
        self.pos1 = str(list(range(self.cui1_pos, 0, -1)) + list(range(len(text_segment)-self.cui1_pos)))
        self.pos2 = str(list(range(self.cui2_pos, 0, -1)) + list(range(len(text_segment)-self.cui2_pos)))
        text_segment[self.cui1_pos] = cui_masks.split('|')[0]
        text_segment[self.cui2_pos] = cui_masks.split('|')[1]
        self.text = ' '.join(text_segment)

        self.cui1 = cui_eps.split('|')[0]
        self.cui2 = cui_eps.split('|')[1]
        self.cui1_type = cui_types.split('|')[0]
        self.cui2_type = cui_types.split('|')[1]
        try:
            self.word_count = len(self.text.split('<sep>')[1].split())
        except:
            self.word_count = -1
        return self.__str__()

    def get_subtext(self):
        text_segment = self.text.split()
        cui1_context_cui2 = ' '.join(text_segment[min(self.cui1_pos, self.cui2_pos)+1: max(self.cui1_pos, self.cui2_pos)])
        return cui1_context_cui2


class neg_sample_generator_1():
    def __init__(self, pos_sents, sub_texts, output_path, eps_sub_dict):
        self.pos_sents = pos_sents
        self.sub_texts = sub_texts
        self.output_path = output_path
        self.eps_sub_dict = eps_sub_dict
        self.neg_sents = []
    
    def generate_sample(self):
        sub_texts =  np.random.choice(self.sub_texts, len(self.pos_sents))
        cuis_info_id = np.random.choice(range(len(cuis_info)), len(self.pos_sents))

        for i in tqdm(range(len(self.pos_sents))):
            pos_sent = self.pos_sents[i]
            old_eps = pos_sent.get_eps()
            cui_info = eps_sub_dict[old_eps]
            neg_sent = pos_sent.process(sub_texts[i], cui_info)
            self.neg_sents.append(neg_sent)

    def write_file(self):
        with open(self.output_path, 'w', encoding='utf-8') as file:
            for neg_sent in tqdm(self.neg_sents):
                file.write(str(neg_sent))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("pos_sample_path", type=str)
    parser.add_argument("aug_sample_path", type=str)
    parser.add_argument("neg_sample_path", type=str)
    parser.add_argument("cui_type_list", type=str)
    parser.add_argument("cui_terms_list", type=str)
    parser.add_argument('-t', "--type", type=str, default="diso-anat")
    args = parser.parse_args()
    parameter = parameters()
    np.random.seed(parameter.random_seed)

    sents = []
    sub_texts = []
    cuis_info = []
    old_eps_list = []
    old_masks_list = []
    
    with open(args.pos_sample_path, encoding='utf-8') as pos_file:
        while True:
            line = pos_file.readline()
            if not line:
                break
            parts = line.rstrip('\n').split('|')
            sent = sentence_neg1(parts)
            sents.append(sent)
            eps = sent.get_eps()
            old_eps_list.append(eps)
            masks = sent.get_masks()
            old_masks_list.append(masks)
    old_eps_list = list(set(old_eps_list))
    
    with open(args.aug_sample_path, encoding='utf-8') as aug_file:
        while True:
            line = aug_file.readline()
            if not line:
                break
            parts = line.rstrip('\n').split('|')
            aug_sent = sentence_neg1(parts)
            sub_text = aug_sent.get_subtext()
            sub_texts.append(sub_text)
    

    cleanterms = pd.read_csv(args.cui_terms_list, sep='|')
    cuis = cleanterms[["cui", "sty"]].drop_duplicates().reset_index(drop=True)
    semgroup = pd.read_csv(args.cui_type_list, sep='|', header=None)

    cuis_diso = generate_typed_cui(cuis, semgroup, 'Disorders')
    cuis_anat = generate_typed_cui(cuis, semgroup, 'Anatomy')
    if args.type == 'diso-anat':
        cuis_info = generate_new_eps(cuis_diso, cuis_anat, old_eps_list)
    elif args.type == 'diso-diso':
        print('diso-diso')
        cuis_info = generate_new_eps(cuis_diso, cuis_diso, old_eps_list)

    eps_sub_dict = {old_eps:cui_info for old_eps, cui_info in zip(old_eps_list, cuis_info)}
    new_eps_list = [cui_info[0] for cui_info in cuis_info]
    print(set(old_eps_list).intersection(set(new_eps_list)))

    generator = neg_sample_generator_1(sents, sub_texts, args.neg_sample_path, eps_sub_dict)
    generator.generate_sample()
    generator.write_file()