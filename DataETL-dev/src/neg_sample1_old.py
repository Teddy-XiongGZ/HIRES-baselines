import random
import argparse
import pandas as pd
from parameters import parameters

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


    def process(self, cui_pos_dict=None, transform_cui_dict=None, cui_type_dict=None, type_mask_dict=None, sub_text=None):

        text_segment = self.text.split()
        cui1_cui2 = ' '.join(text_segment[min(self.cui1_pos, self.cui2_pos)+1: max(self.cui1_pos, self.cui2_pos)])

        if sub_text is not None:
            text_segment = text_segment[0: min(self.cui1_pos, self.cui2_pos)+1] + sub_text.split() + text_segment[max(self.cui1_pos, self.cui2_pos):]
            if self.cui1_pos < self.cui2_pos:
                self.cui2_pos = self.cui1_pos + len(sub_text.split()) + 1
            else:
                self.cui1_pos = self.cui2_pos + len(sub_text.split()) + 1
            self.pos1 = str(list(range(self.cui1_pos, 0, -1)) + list(range(len(text_segment)-self.cui1_pos)))
            self.pos2 = str(list(range(self.cui2_pos, 0, -1)) + list(range(len(text_segment)-self.cui2_pos)))

            cui_pair = self.cui1 + '|' + self.cui2
            cui_pos = cui_pos_dict[cui_pair]
            new_cui_pairs = transform_cui_dict[cui_pair]

            if cui_pos == 1:
                self.cui1 = new_cui_pairs.split('|')[0]
                self.cui1_type = cui_type_dict[new_cui_pairs].split('|')[0]
                text_segment[self.cui1_pos] = type_mask_dict[self.cui1_type]
            else:
                self.cui2 = new_cui_pairs.split('|')[1]
                self.cui2_type = cui_type_dict[new_cui_pairs].split('|')[1]
                text_segment[self.cui2_pos] = type_mask_dict[self.cui2_type]
            self.text = ' '.join(text_segment)
            try:
                self.word_count = len(self.text.split('<sep>')[1].split())
            except:
                self.word_count = -1
        return cui1_cui2

    def __str__(self):
        return self.id + '|' + self.rank + '|' + self.cui1 + '|' + self.cui1_type + '|' + self.cui2 + '|' \
                + self.cui2_type + '|' + self.text + '|' + self.article_structure + '|' + self.pos1 + '|' \
                + self.pos2 + '|' + str(self.word_count) + '|' + self.is_title1 + '|' + self.is_title2 + '\n'


class negsample1_generator:
    def __init__(self, positive_sent, augment_sent):
        self.sent = positive_sent
        self.augment_sent = augment_sent

    def process(self, cui_pos_dict, transform_cui_dict, cui_type_dict, type_mask_dict):
        sub_text = self.augment_sent.process()
        self.sent.process(cui_pos_dict, transform_cui_dict, cui_type_dict, type_mask_dict, sub_text)
        return self.sent


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("pos_sample_path", type=str)
    parser.add_argument("aug_sample_path", type=str)
    parser.add_argument("neg_sample_path", type=str)
    parser.add_argument("cui_type_list", type=str)
    args = parser.parse_args()
    parameter = parameters()

    pos_sents = []
    aug_sents = []
    neg_sents = []
    random.seed(parameter.random_seed)

    #New_start
    cui_pairs = []
    cui_type_pairs = []
    with open(args.pos_sample_path, 'r') as sent:
        while True:
            line = sent.readline()
            if not line:
                break
            parts = line.split("|")
            cui_pair = parts[2] + "|" + parts[4]
            cui_type_pair = parts[3] + '|' + parts[5]
            cui_pairs.append(cui_pair)
            cui_type_pairs.append(cui_type_pair)

    df = pd.DataFrame({"cui_pair": cui_pairs, "cui_type": cui_type_pairs}).drop_duplicates(["cui_pair"])
    cui_pairs = df["cui_pair"].tolist()
    cui_types = df["cui_type"].tolist()
    cui_type_dict = {cui_pair: cui_type for cui_pair, cui_type in zip(cui_pairs, cui_types)}

    cui_types = []
    cui_masks = []
    with open(args.cui_type_list, 'r') as type_lists:
        while True:
            line = type_lists.readline()
            if not line:
                break
            parts = line.split("|")
            cui_type = parts[3].rstrip()
            cui_mask = parts[2].lower()
            cui_types.append(cui_type)
            cui_masks.append(cui_mask)
    type_mask_dict = {cui_type: cui_mask for cui_type, cui_mask in zip(cui_types, cui_masks)}

    match_idx = [random.randint(0, len(cui_pairs)-1) for i in range(len(cui_pairs))]
    cui_pos = [random.randint(1, 2) for i in range(len(cui_pairs))]
    cui_pos_dict = {cui_pair:pos for cui_pair, pos in zip(cui_pairs, cui_pos)}
    transform_cui_dict = {cui_pairs[i]:cui_pairs[match_idx[i]] for i in range(len(cui_pairs))}

    # New_end

    with open(args.pos_sample_path, 'r') as file:
        while True:
            pos_sent = file.readline()
            if not pos_sent or pos_sent is None:
                break
            pos_sent_segment = pos_sent.rstrip('\n').split('|')
            pos_sents.append(sentence(pos_sent_segment))

    with open(args.aug_sample_path, 'r') as file:
        while True:
            aug_sent = file.readline()
            if not aug_sent or pos_sent is None:
                break
            aug_sent_segment = aug_sent.rstrip('\n').split('|')
            aug_sents.append(sentence(aug_sent_segment))

    for pos_sent in pos_sents:
        sample_id = random.randint(0, len(pos_sents) - 1)
        aug_sent = aug_sents[sample_id]

        neg_sample_generator = negsample1_generator(pos_sent, aug_sent)
        neg_sents.append(neg_sample_generator.process(cui_pos_dict, transform_cui_dict, cui_type_dict, type_mask_dict))

    with open(args.neg_sample_path, 'w') as file:
        for neg_sent in neg_sents:
            file.write(str(neg_sent))