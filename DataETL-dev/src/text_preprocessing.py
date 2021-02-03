import string
from scipy.sparse import csr_matrix, hstack
import pickle
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer, TfidfVectorizer
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import json
import random
from sklearn.preprocessing import StandardScaler, MinMaxScaler, MaxAbsScaler
# import gc

# import pdb

random.seed(0)

EMBEDDING_SIZE = 100
PADDING_SIZE = 50
FEATURE_SIZE = 40000 

class EPItem:
    def __init__(self, arg_list):
        self.cui1 = arg_list[0]
        self.cui2 = arg_list[1]
        self.sentences = arg_list[2]
        self.label = arg_list[3]
        self.cui1_info = np.array(json.loads(arg_list[4])) if arg_list[4] is not None else None
        self.cui2_info = np.array(json.loads(arg_list[5])) if arg_list[5] is not None else None
        self.length = len(self.sentences)
        self.array = None

    def getdata(self):
        return self.array#.A.astype(np.float32)

    def getlabel(self):
        return self.label

    def getalllabel(self):
        return np.array([self.label]*self.length)

    def __len__(self):
        return self.length



def getsentences(epitem_list):
    sentences = []
    for item in epitem_list:
        sentences += item.sentences
    return sentences

# def mapX2epitem(epitem_list, X):
#     i = 0
#     for item in epitem_list:
#         cui1_info = item.cui1_info
#         cui2_info = item.cui2_info
#         if cui1_info is not None and cui2_info is not None:
#             tmp = X[i:i+item.length].copy()
#             cui_info = np.hstack([np.tile(cui1_info, (tmp.shape[0],1)), np.tile(cui2_info, (tmp.shape[0],1))])
#             if cui_info.shape[1] != 2000:
#                 print(cui1_info, cui2_info)
#             item.array = hstack((tmp, csr_matrix(cui_info)))
#         else:
#             item.array = X[i:i+item.length]
#         i += item.length

def mapX2epitem(epitem_list, X):
    i = 0
    # pdb.set_trace()
    for item in epitem_list:
        # gc.collect()
        cui1_info = item.cui1_info
        cui2_info = item.cui2_info
        if cui1_info is not None and cui2_info is not None:
            tmp = X[i:i+item.length].copy()
            cui_info = np.hstack([np.tile(cui1_info, (tmp.shape[0],1)), np.tile(cui2_info, (tmp.shape[0],1))])
            if cui_info.shape[1] != 2000:
                print(cui1_info, cui2_info)
            item.array = hstack((tmp, csr_matrix(cui_info)))
        else:
            item.array = X[i:i+item.length]
        i += item.length
    # pdb.set_trace()
    # print(i)

# def text_preprocessing(POS_SAMPLE_PATH, NEG_SAMPLE_PATH, model, cui_info=None):
def text_preprocessing(SAMPLE_PATHS, model, cui_info=None):
    if cui_info is not None:
        print("loading cui info")
        with open(cui_info, "rb") as f:
            embed_dic = pickle.load(f)
        print("done")

    sample_paths = SAMPLE_PATHS

    intab = string.punctuation
    outtab = "                                "
    trantab = str.maketrans(intab, outtab)
    # word_len = 0

    print("--reading samples--")
    samples = []
    for path in sample_paths:
        with open(path, 'r') as file:
            while True:
                # gc.collect()
                line = file.readline()
                if not line:
                    break
                line_list = line.split('|')
                cui1 = line_list[0]
                cui2 = line_list[1]
                sentences = json.loads(line_list[2])
                # if model=='SVM' or model=='RF':
                #     if len(sentences) > 10:
                #         sentences = random.sample(sentences, 10)
                if model=='SVM' or model=='RF' or model=='NB':
                    if len(sentences) > 10:
                        sentences = random.sample(sentences, 10)
                if model=='CNN':
                    if len(sentences) > 10:
                        sentences = random.sample(sentences, 10)
                label = int(line_list[8])
                if cui_info is not None:
                    item = EPItem([cui1, cui2, sentences, label, 
                        embed_dic[cui1] if cui1 in embed_dic else embed_dic['empty'], 
                        embed_dic[cui2] if cui2 in embed_dic else embed_dic['empty']])
                else:
                    item = EPItem([cui1, cui2, sentences, label, None, None])
                
                # min = -4.23762
                # if model == 'NB':
                #     if item.cui1_info is not None and item.cui2_info is not None:
                #         item.cui1_info = item.cui1_info + 4.5
                #         item.cui2_info = item.cui2_info + 4.5
                samples.append(item)
    print("--done--")

    print("--extracting features from texts--")
    # if model=='NB' or model=='SVM' or model=='RF':
        # tfidfvect = TfidfVectorizer(stop_words='english', max_features=FEATURE_SIZE)
        # X = tfidfvect.fit_transform(getsentences(samples))
        # if model=='SVM':
        #     scaler = MaxAbsScaler()
        #     scaler.fit(X)
        #     X = scaler.transform(X)
        # print(X.shape)
        # mapX2epitem(samples, X)
    # if model=='CNN':
    #     tokenizer = Tokenizer(num_words=None)
    #     tokenizer.fit_on_texts(getsentences(samples))
    #     word_list = tokenizer.word_index
    #     word_len = len(word_list) + 20
    #     corpus_seq = tokenizer.texts_to_sequences(getsentences(samples))
    #     corpus_seq = pad_sequences(corpus_seq, maxlen=PADDING_SIZE)
    #     X = np.array(corpus_seq)
    #     mapX2epitem(samples, X)
        
    Y = np.array([item.label for item in samples])
    print("--done--")

    return samples, Y
