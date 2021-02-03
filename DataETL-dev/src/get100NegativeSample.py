# %%
from sklearn.model_selection import train_test_split
import random
import pickle
import pandas as pd
random.seed(0)
disodiso_pos_file = '../data/positive_sample_diso_diso.txt'
disodiso_neg1_file = '../data/negative_sample1_diso_diso.txt'
disodiso_neg2_file = '../data/negative_sample3_diso_diso.txt'
disoanat_pos_file = '../data/positive_sample_2.txt'
disoanat_neg1_file = '../data/negative_sample1.txt'
disoanat_neg2_file = '../data/negative_sample3.txt'
cui2term_file = '/media/sda1/ChenYulin/cleanterms/cui2preferredterm.pkl'

# %%
def get_samples(filepath):
    samples = []
    with open(filepath)as f:
        line = f.readline()
        while line:
            line_list = line.split('|')
            samples.append((line_list[0], line_list[1], int(line_list[-2])))
            line = f.readline()
    return samples

def get_negative_sample_in_testset(positive_sample_file, negative_sample_file):
    all_samples = get_samples(positive_sample_file) + get_samples(negative_sample_file)
    _, test_samples, _, _ = train_test_split(all_samples, [0]*len(all_samples), test_size=0.2, random_state=0)
    negative_test_samples = list(filter(lambda x: x[-1] == 0, test_samples))
    return negative_test_samples

def get_100_negative_samples(positive_sample_file, negative_sample_file_list):
    negative_test_samples = []
    for negative_sample_file in negative_sample_file_list:
        negative_test_samples += get_negative_sample_in_testset(positive_sample_file, negative_sample_file)
    negative_test_samples = list(set(negative_test_samples))
    negative_test_samples_100 = random.sample(negative_test_samples, 100)
    return negative_test_samples_100
# %%
disodiso_neg_100 = get_100_negative_samples(disodiso_pos_file, [disodiso_neg1_file, disodiso_neg2_file])
# %%
disoanat_neg_100 = get_100_negative_samples(disoanat_pos_file, [disoanat_neg1_file, disoanat_neg2_file])
# %%
def generate_negative_sample_detail_csv(negative_sample, target_file):
    with open(cui2term_file, 'rb')as f:
        cui2term = pickle.load(f)
    cui1 = []
    cui2 = []
    term1 = []
    term2 = []
    for sample in negative_sample:
        cui1.append(sample[0])
        cui2.append(sample[1])
        term1.append(cui2term.get(sample[0]))
        term2.append(cui2term.get(sample[1]))
    data = {'cui1': cui1, 'term1':term1, 'cui2':cui2, 'term2':term2}
    data = pd.DataFrame(data)
    data.to_csv(target_file, index=False)
    return

# %%
generate_negative_sample_detail_csv(disodiso_neg_100, '../data/disodiso_test_neg_100.csv')
# %%
generate_negative_sample_detail_csv(disoanat_neg_100, '../data/disoanat_test_neg_100.csv')
# %%
# generate overlapping cuis
def get_cui1_cui2(sample_list):
    cui1 = [sample[0] for sample in sample_list]
    cui2 = [sample[1] for sample in sample_list]
    return cui1, cui2

def get_sample_list(positive_sample_file, negative_sample_file):
    all_samples = get_samples(positive_sample_file) + get_samples(negative_sample_file)
    train_samples, test_samples, _, _ = train_test_split(all_samples, [0]*len(all_samples), test_size=0.2, random_state=0)
    negative_test_samples = list(filter(lambda x: x[-1] == 0, test_samples))
    positive_test_samples = list(filter(lambda x: x[-1] == 1, test_samples))
    negative_train_samples = list(filter(lambda x: x[-1] == 0, train_samples))
    positive_train_samples = list(filter(lambda x: x[-1] == 1, train_samples))
    return positive_train_samples, positive_test_samples, negative_train_samples, negative_test_samples

# %%
positive_train_samples, positive_test_samples, negative_train_samples, negative_test_samples = get_sample_list(disoanat_pos_file, disoanat_neg2_file)

# %%
def get_overlapped_cuis(sample_list1, sample_list2, filename):
    diso1, anat1 = get_cui1_cui2(sample_list1)
    diso2, anat2 = get_cui1_cui2(sample_list2)
    diso_overlap = list(set(diso1).intersection(set(diso2)))
    anat_overlap = list(set(anat1).intersection(set(anat2)))
    types = ['DISO'] * len(diso_overlap) + ['ANAT'] * len(anat_overlap)
    cuis = diso_overlap + anat_overlap
    with open(cui2term_file, 'rb')as f:
        cui2term = pickle.load(f)
    terms = [cui2term.get(cui) for cui in cuis]
    data = {'cui': cuis, 'term':terms, 'type':types}
    data = pd.DataFrame(data)
    data.to_csv(filename, index=False)
    print(len(diso_overlap), len(anat_overlap), filename)
    print(len(list(set(diso1))), len(list(set(anat1))), len(list(set(diso2))), len(list(set(anat2))))
    return
# %%
get_overlapped_cuis(positive_train_samples, positive_test_samples, 'positive_train-positive_test_overlap_3.csv')
get_overlapped_cuis(positive_train_samples, negative_train_samples, 'positive_train-negative_train_overlap_3.csv')
get_overlapped_cuis(positive_train_samples, negative_test_samples, 'positive_train-negative_test_overlap_3.csv')
get_overlapped_cuis(positive_test_samples, negative_test_samples, 'positive_test-negative_test_overlap_3.csv')
get_overlapped_cuis(positive_test_samples, negative_train_samples, 'positive_test-negative_train_overlap_3.csv')
get_overlapped_cuis(negative_test_samples, negative_train_samples, 'negative_test-negative_train_overlap_3.csv')

# %%
