import argparse
from NB_SVM import nb_svm
from text_preprocessing import text_preprocessing
from Text_CNN import text_cnn

import gc, sys, os, psutil

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("sample1_path", type=str)
    parser.add_argument("sample2_path", type=str)
    parser.add_argument("model", type=str)
    parser.add_argument("result_log", type=str)
    parser.add_argument("--split", type=int, default=0)
    parser.add_argument("--embed_dic_path", type=str, default=None)
    parser.add_argument("-d", '--device', type=str, default='cpu')
    args = parser.parse_args()

    if args.model=='NB' or args.model=='SVM' or args.model == "RF":
        if args.split:
            X_train, Y_train = text_preprocessing([args.sample1_path], args.model, args.embed_dic_path)
            X_val, Y_val = text_preprocessing([args.sample2_path], args.model, args.embed_dic_path)
            nb_svm(X_train, Y_train, args.model, args.result_log, X_val, Y_val)
        else:
            X, Y = text_preprocessing([args.sample1_path, args.sample2_path], args.model, args.embed_dic_path)
            nb_svm(X, Y, args.model, args.result_log)
    if args.model=='CNN':
        if args.split:
            X_train, Y_train = text_preprocessing([args.sample1_path], args.model)
            X_val, Y_val = text_preprocessing([args.sample2_path], args.model)
            text_cnn(X_train, Y_train, args.result_log, args.device, X_val, Y_val)
        else:
            X, Y = text_preprocessing([args.sample1_path, args.sample2_path], args.model)
            text_cnn(X, Y, args.result_log, args.device)
        # X, Y, word_len = text_preprocessing(args.sample1_path, args.sample2_path, args.model)
        # text_cnn(X, Y, word_len, args.result_log, args.device)
