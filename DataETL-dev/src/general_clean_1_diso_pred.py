from LoadSentence import LoadSentences, Sentence
from LoadTypelist import LoadTypelist
from tqdm import tqdm
import json
import argparse
from multiprocessing import Process
parser = argparse.ArgumentParser()
parser.add_argument('type_path', action='store', type=str,
                    help='The path to load cui types')

parser.add_argument('input_file', action='store', type=str,
                    help='The path to load sentences')

parser.add_argument('output_file', action='store', type=str,
                    help='The path to save general clean result')

parser.add_argument('exception_path', action='store', type=str,
                    help='The path to output exception')


args = parser.parse_args()
type_path = args.type_path
sentence_path = args.input_file
save_path = args.output_file
exception_path = args.exception_path


class Cleaner:
    def __init__(self, sentence_path, type_path, save_path, exception_path, pos_cui1_list):
        self.sentence_path = sentence_path
        self.type_path = type_path
        self.save_path = save_path
        self.exception_path = exception_path
        self.sentence_list = []
        self.pos_cui1_list = pos_cui1_list

    def init(self):
        sentloader = LoadSentences(self.sentence_path)
        typeloader = LoadTypelist(self.type_path)
        print('- loading sentence...')
        self.reader = sentloader.Reader()
        print('- done')
        print('- loading type list...')
        self.type_dic = typeloader.Load()
        print('- done')


    def Process(self):
        with open(self.save_path, 'w')as outfile:
            with open(self.exception_path, 'w') as exception_file:
                for sentence in tqdm(self.reader):
                    if sentence.cui1 in self.pos_cui1_list:
                        if sentence.is_proper_sentence:
                            if sentence.entity_in_sent:
                                mask1 = self.type_dic[sentence.type1]
                                mask2 = self.type_dic[sentence.type2]
                                sentence.mask([mask1, mask2])
                                sentence.calculate_pos()
                                outfile.writelines(str(sentence))
                        else:
                            exception_file.writelines(sentence.text+'\n')

def GeneralClean(index, cui1_list):

    cleaner = Cleaner(sentence_path+str(index)+'.txt', type_path, save_path+str(index)+'.txt', exception_path+str(index)+'.txt', cui1_list)
    cleaner.init()
    cleaner.Process()

if __name__ == '__main__':
    cui1_list = []
    f1 = '/media/sda1/RelationExtraction/DataETL-dev/data/positive_sample_diso_diso.txt'
    with open(f1)as f:
        line = f.readline()
        while line.strip():
            line_list = line.split('|')
            cui1 = line_list[0]
            cui1_list.append(cui1)
            line = f.readline()
    cui1_list = list(set(cui1_list))
    plist = []
    for i in range(9):
        p = Process(target=GeneralClean,args = (i,cui1_list,))
        p.start()
        plist.append(p)
    for ap in plist:
        ap.join()
    #GeneralClean(cui1_list)