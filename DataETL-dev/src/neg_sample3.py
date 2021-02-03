import json
import numpy as np
import pandas as pd
import argparse
from tqdm import tqdm
from parameters import parameters
from read_sentence import *


class sentence_neg3(sentence):
    def __init__(self, input_segment):
        super().__init__(input_segment)

    def embedding(self, idx_table, vec_table):
        words = self.text.split()
        words_idx = []
        for word in words:
            if word in idx_table:
                word_idx = idx_table[word]
            else:
                word_idx = 0
            words_idx.append(word_idx)
        words_vec = [vec_table[word_idx] for word_idx in words_idx]
        sent_vec = np.mean(words_vec, axis=0)
        self.embed = sent_vec / np.linalg.norm(sent_vec)
        return self.embed

    def cui_substitute(self, cui_info, idx_table, vec_table):
        (cui_eps, cui_masks, cui_types) = cui_info
        text_segment = self.text.split()
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

        self.embed = self.embedding(idx_table, vec_table)


class entity_pair:
    def __init__(self, cui1_cui2, cui_types):
        self.cui1_cui2 = cui1_cui2
        self.cui_types = cui_types
        self.entity_embed = None
        self.sents = []

    def add_sent(self, sent):
        self.sents.append(sent)

    def entity_embedding(self):
        sent_vec_list = [sent.embed * int(sent.word_count) for sent in self.sents]  # weighting average
        entity_vec = np.mean(sent_vec_list, axis=0)
        self.entity_embed = entity_vec / np.linalg.norm(entity_vec)

    def entity_cui_substitute(self, cui_info, idx_table, vec_table):
        for sent in self.sents:
            sent.cui_substitute(cui_info, idx_table, vec_table)


class negsample3_generator:
    def __init__(self, pos_samples_matrix, candidate_samples_matrix, idx_samples):
        self.pos_samples_matrix = pos_samples_matrix
        self.candidate_neg_matrix = candidate_samples_matrix
        self.idx_samples = idx_samples
        self.id_dict = {}   # key: pos_sample  value: list of neg_samples

    def process(self, candidate_neg_samples, sample_nums):
        print("--drawing sentences--")
        result = np.matmul(self.candidate_neg_matrix, self.pos_samples_matrix)
        arg_max_id = np.argmax(result, axis=1)
        sim = result[range(len(arg_max_id)), arg_max_id]
        neg_id = np.argsort(-sim)[0:sample_nums].tolist()
        neg_samples = []
        for id in neg_id:
            neg_sample = candidate_neg_samples[self.idx_samples[id]]
            neg_samples.append(neg_sample)
            if arg_max_id[id] not in self.id_dict.keys():
                self.id_dict[arg_max_id[id]] = []
            self.id_dict[arg_max_id[id]].append(id)
        return neg_samples


def entity_pair_merge(path, word2idx, idx2vec, type_mask_dict):
    cui1_cui2_dict = {}
    idx_pairs_dict = {}
    cui_masks_list = []
    with open(path, 'r', encoding='utf-8') as file:
        count = 0
        while True:
            sent = file.readline()
            if not sent:
                break
            sent_segment = sent.rstrip('\n').split('|')
            cui1_cui2 = str(sent_segment[2]) + '|' + str(sent_segment[4])
            cui_types = str(sent_segment[3]) + '|' + str(sent_segment[5])
            cui_masks = type_mask_dict[str(sent_segment[3])] + '|' + type_mask_dict[str(sent_segment[5])]
            if cui1_cui2 not in cui1_cui2_dict.keys():
                cui1_cui2_dict[cui1_cui2] = entity_pair(cui1_cui2, cui_types)
                idx_pairs_dict[count] = cui1_cui2
                cui_masks_list.append(cui_masks)
                count = count + 1
            pos_sent = sentence_neg3(sent_segment)
            pos_sent.embedding(word2idx, idx2vec)
            cui1_cui2_dict[cui1_cui2].add_sent(pos_sent)
    return cui1_cui2_dict, idx_pairs_dict, cui_masks_list


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("candidate_sample_path", type=str)
    parser.add_argument("positive_sample_path", type=str)
    parser.add_argument("output_negative_sample", type=str)
    parser.add_argument("index_file_path", type=str)
    parser.add_argument("word_embed_path", type=str)
    parser.add_argument("cui_type_list", type=str)
    parser.add_argument("cui_terms_list", type=str)
    parser.add_argument("-n", "--sample_number", type=int, default=5000)
    parser.add_argument('-t', "--type", type=str, default="diso-anat")
    args = parser.parse_args()
    parameter = parameters()
    np.random.seed(parameter.random_seed)

    cleanterms = pd.read_csv(args.cui_terms_list, sep='|')
    cuis = cleanterms[["cui", "sty"]].drop_duplicates().reset_index(drop=True)
    semgroup = pd.read_csv(args.cui_type_list, sep='|', header=None)
    type_mask_dict = {row[3]:row[2].lower() for id,row in semgroup.iterrows()}

    cuis_diso = generate_typed_cui(cuis, semgroup, 'Disorders')
    cuis_anat = generate_typed_cui(cuis, semgroup, 'Anatomy')

    with open(args.index_file_path, 'r') as f:
        word2idx = json.load(f)
    idx2vec = np.load(args.word_embed_path)

    print("--positive samples merging--")
    pos_samples, pos_idx_samples, old_mask_list = entity_pair_merge(
        args.positive_sample_path, word2idx, idx2vec, type_mask_dict)
    print("--candidate negative samples merging--")
    candidate_neg_samples, candidate_idx_samples, _ = entity_pair_merge(
        args.candidate_sample_path, word2idx, idx2vec, type_mask_dict)
    pos_sample_nums = len(pos_samples.keys())
    candidate_sample_nums = len(candidate_neg_samples.keys())

    old_eps_list = np.random.choice(list(pos_samples.keys()), candidate_sample_nums)
    if args.type == 'diso-anat':
        cuis_info = generate_new_eps(cuis_diso, cuis_anat, old_eps_list)
    elif args.type == 'diso-diso':
        print('diso-diso')
        cuis_info = generate_new_eps(cuis_diso, cuis_diso, old_eps_list)
    else:
        assert(0==1)

    for i in tqdm(range(candidate_sample_nums)):
        candidate_neg_samples[candidate_idx_samples[i]].entity_cui_substitute(cuis_info[i], word2idx, idx2vec)

    pos_sample_vec_list = []
    candidate_neg_sample_vec_list = []

    print("--similarity measuring--")
    for key in pos_samples.keys():
        pos_sample = pos_samples[key]
        pos_sample.entity_embedding()
        pos_sample_vec_list.append(pos_sample.entity_embed)
    for key in candidate_neg_samples.keys():
        candidate_neg_sample = candidate_neg_samples[key]
        candidate_neg_sample.entity_embedding()
        candidate_neg_sample_vec_list.append(candidate_neg_sample.entity_embed)

    pos_samples_matrix = np.array(pos_sample_vec_list).T
    candidate_samples_matrix = np.array(candidate_neg_sample_vec_list)

    model = negsample3_generator(pos_samples_matrix, candidate_samples_matrix, candidate_idx_samples)
    neg_samples = model.process(candidate_neg_samples, args.sample_number)

    print("--result outputing--")
    with open(args.output_negative_sample, 'w', encoding='utf-8') as file:
        for neg_sample in neg_samples:
            for sent in neg_sample.sents:
                file.write(str(sent))