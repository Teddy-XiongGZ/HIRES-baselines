import re
import random
import argparse
import pandas as pd

class sentence:
    def __init__(self, input_segment):
        self.id = input_segment[0]
        self.rank = input_segment[1]
        self.cui1 = input_segment[2]
        self.cui1_type = input_segment[3]
        self.cui2 = input_segment[4]
        self.cui2_type = input_segment[5]
        self.text = input_segment[6].replace(u'\xa0', u' ').replace(u'\u200a', u' ').replace(u'\u2009', u' ')
        self.article_structure = input_segment[7]
        self.pos1 = eval(input_segment[8])
        self.pos2 = eval(input_segment[9])
        self.word_count = input_segment[10]
        self.is_title1 = input_segment[11]
        self.is_title2 = input_segment[12]
        self.cui1_pos = self.pos1[0]
        self.cui2_pos = self.pos2[0]

    def process(self, cui_pos=None, cui_pairs=None, match_idx=None, cui_type_dict=None, type_mask_dict=None):

        text_segment = self.text.split()
        cui_pair = self.cui1 + '|' + self.cui2
        cui_pair_id = cui_pairs.index(cui_pair)
        new_cui_pairs = cui_pairs[match_idx[cui_pair_id]]
        if cui_pos[cui_pair_id] == 1:
            self.cui1 = new_cui_pairs.split('|')[0]
            self.cui1_type = cui_type_dict[new_cui_pairs].split('|')[0]
            text_segment[self.cui1_pos] = type_mask_dict[self.cui1_type]
        else:
            self.cui2 = new_cui_pairs.split('|')[1]
            self.cui2_type = cui_type_dict[new_cui_pairs].split('|')[1]
            text_segment[self.cui2_pos] = type_mask_dict[self.cui2_type]
        text_segment[self.cui1_pos], text_segment[self.cui2_pos] = text_segment[self.cui2_pos], text_segment[self.cui1_pos]
        self.text = ' '.join(text_segment)

    def __str__(self):
        neg_sent = self.id + '|' + self.rank + '|' + self.cui1 + '|' + self.cui1_type + '|' + self.cui2 + '|' + \
                         self.cui2_type + '|' + self.text + '|' + self.article_structure + '|' + str(self.pos1) + '|' + \
                         str(self.pos2) + '|' + self.word_count + '|' + self.is_title1 + '|' + self.is_title2
        return neg_sent


class negsample2_generator:
    def __init__(self, positive_path, negative_path, cui_list_path):
        self.positive_path = positive_path
        self.negative_path = negative_path
        self.cui_list_path = cui_list_path
        self.cui_pairs = []
        self.cui_type_dict = None

    def reader(self):
        self.cui_pairs = []
        cui_type_pairs = []
        with open(self.positive_path, 'r') as sent:
            while True:
                line = sent.readline()
                if not line:
                    break
                parts = line.split("|")
                cui_pair = parts[2] + "|" + parts[4]
                cui_type_pair = parts[3] + '|' + parts[5]
                self.cui_pairs.append(cui_pair)
                cui_type_pairs.append(cui_type_pair)

        df = pd.DataFrame({"cui_pair": self.cui_pairs, "cui_type": cui_type_pairs}).drop_duplicates(["cui_pair"])
        self.cui_pairs = df["cui_pair"].tolist()
        cui_types = df["cui_type"].tolist()
        self.cui_type_dict = {cui_pair: cui_type for cui_pair, cui_type in zip(self.cui_pairs, cui_types)}

        cui_types = []
        cui_masks = []
        with open(self.cui_list_path, 'r') as type_lists:
            while True:
                line = type_lists.readline()
                if not line:
                    break
                parts = line.split("|")
                cui_type = parts[3].rstrip()
                cui_mask = parts[2].lower()
                cui_types.append(cui_type)
                cui_masks.append(cui_mask)
        self.type_mask_dict = {cui_type: cui_mask for cui_type, cui_mask in zip(cui_types, cui_masks)}
        self.match_idx = [random.randint(0, len(self.cui_pairs) - 1) for i in range(len(self.cui_pairs))]
        self.cui_pos = [random.randint(1, 2) for i in range(len(self.cui_pairs))]


    def process(self):
        with open(self.positive_path) as pos_file, open(self.negative_path, 'w') as neg_file:
            while True:
                line = pos_file.readline()
                if not line:
                    break
                line = line.split('|')
                pos_sent = sentence(line)
                pos_sent.process(self.cui_pos, self.cui_pairs, self.match_idx, self.cui_type_dict, self.type_mask_dict)
                neg_file.write(str(pos_sent))



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("positive_sample_path", type=str)
    parser.add_argument("negative_sample_path", type=str)
    parser.add_argument("cui_type_list", type=str)
    args = parser.parse_args()
    random.seed(1)

    negsample_generator = negsample2_generator(args.positive_sample_path, args.negative_sample_path, args.cui_type_list)
    negsample_generator.reader()
    negsample_generator.process()