import os
import argparse
import numpy as np
from time import time

import data_path
from bert_serving.client import BertClient
from bert_data import BertTextLoader


parser = argparse.ArgumentParser()
parser.add_argument('input_file', action='store', type=str,
                    help='The path to the input file')

parser.add_argument('output_file', action='store', type=str,
                    help='The path to the output embedding')

parser.add_argument('-t', dest='use_title', action='store_true')

args = parser.parse_args()
input_file = args.input_file
output_file = args.output_file
use_title = args.use_title or False

def print_text_statistics(l):
    p50 = np.percentile(l, 50)
    p90 = np.percentile(l, 90)
    p99 = np.percentile(l, 99)
    mean = np.mean(l)
    max_len = np.max(l)
    min_len = np.min(l)
    print("Text length statistics:\np50 {}\np90 {}\np99 {}\nmean {}\nmax {}\nmin {}".format(
        p50, p90, p99, mean, max_len, min_len))

def encode():
    path = os.path.join(data_path.DATA_PATH, input_file)
    embedding_path = os.path.join(data_path.DATA_PATH, output_file)
    loader = BertTextLoader(path, use_title=use_title)
    loader.load()

    text_len = []
    sentence_count = 0
    embeddings_by_pair = []
    bc = BertClient(check_length=False)
    start_time = time()
    for i, sentence_list in enumerate(loader):
        if len(sentence_list) > 0:
            # sentence_len_list = [len(l.split(' ')) for l in sentence_list]
            # text_len.extend(sentence_len_list)
            embeddings = bc.encode(sentence_list)
            embeddings_by_pair.append(embeddings.copy())
            sentence_count += len(sentence_list)
        else:
            raise Exception("Entity pair index at {} has no corresponding sentences".format(i))
    bc.close()
    # print_text_statistics(text_len)
    duration = time() - start_time
    embeddings_by_pair = np.array(embeddings_by_pair)
    np.save(embedding_path, embeddings_by_pair)
    print("[INFO] bert embedding saved to {}.npy as numpy.ndarray".format(embedding_path))
    print("[INFO] Done encoding {} senteces in {} seconds.\n".format(sentence_count, duration))

if __name__ == '__main__':
    encode()
