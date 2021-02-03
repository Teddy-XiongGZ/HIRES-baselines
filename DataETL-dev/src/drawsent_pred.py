from LoadNER import LoadNERs
from Trie_entitypair import Trie,TrieNode
from tqdm import tqdm
from multiprocessing import Process
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('db_name', action='store', type=str,
                    help='The database where cui pairs are stored')

parser.add_argument('table_name', action='store', type=str,
                    help='The table where cui pairs are stored')

parser.add_argument('save_path', action='store', type=str,
                    help='The path to save trie_ep')

parser.add_argument('NER_file', action='store', type=str,
                    help='The path to input NER')

parser.add_argument('sent_file', action='store', type=str,
                    help='The path to input sentences')

parser.add_argument('output_file', action='store', type=str,
                    help='The path to output file')

parser.add_argument('num', action='store', type=int,
                    help='num of sentence files to process')

args = parser.parse_args()
db_name = args.db_name
table_name = args.table_name
save_path = args.save_path
load_path = args.save_path
NER_file = args.NER_file
sent_file = args.sent_file
output_file = args.output_file
num = args.num

type1 = ['Acquired Abnormality','Anatomical Abnormality' ,'Molecular Dysfunction' ,'Congenital Abnormality' ,
'Disease or Syndrome' ,'Experimental Model of Disease' ,'Injury or Poisoning' ,
'Mental or Behavioral Dysfunction' ,'Neoplastic Process','Pathologic Function' ,'Sign or Symptom']
type2 = type1

class TitleSent:
    def __init__(self):
        self.titles = {}

    def insert(self, title, entities):
        if title in self.titles:
            if entities in self.titles[title]:
                return False
            else:
                self.titles[title].append(entities)
        else:
            self.titles[title] = [entities]
        return True

class EntityPair:
    def __init__(self, article_id, sent_id, title, text, article_structure, cui1, cui2, cui1_attr, cui2_attr, title_sent):
        self.article_id = article_id
        self.sent_id = sent_id
        self.begin1 = cui1_attr[0]
        self.end1 = cui1_attr[1]
        self.cui1 = cui1
        self.entity1 = cui1_attr[2]
        self.cui1_type = cui1_attr[3]
        self.is_title1 = int(cui1_attr[4])
        self.begin2 = cui2_attr[0]
        self.end2 = cui2_attr[1]
        self.cui2 = cui2
        self.entity2 = cui2_attr[2]
        self.cui2_type = cui2_attr[3]
        self.is_title2 = int(cui2_attr[4])
        if self.is_title1 and self.is_title2:
            self.text = title
            self.title = '<EMPTY_TITLE>'
            self.article_structure = ' . . . '
            if title_sent.insert(title, [self.entity1, self.entity2]):
                self.is_entitypair = 1
                self.is_title1 = 0
                self.is_title2 = 0
            else:
                self.is_entitypair = 0
        elif (self.is_title1 and title == self.entity1) or \
            (self.is_title2 and title == self.entity2) or \
            (not self.is_title1 and not self.is_title2):
            self.title = title
            self.text = text
            self.article_structure = article_structure
            self.is_entitypair = 1
        else:
            self.is_entitypair = 0



    def __str__(self):
        return str(self.article_id)+'|' +str(self.sent_id)+'|' + str(self.title)+'|'+str(self.text)+'|'+str(self.article_structure)+\
            '|'+str(self.begin1)+'|'+str(self.end1)+'|'+str(self.entity1)+'|'+str(self.cui1)+'|'\
            +str(self.cui1_type)+'|'+str(self.is_title1)+'|'+str(self.begin2)+'|'+str(self.end2)+'|'\
            +str(self.entity2)+'|'+str(self.cui2)+'|'+str(self.cui2_type)+'|'+str(self.is_title2)  +'\n'



class GenerateEntityPair:
    def __init__(self, db_name, table_name, save_path, load_path, NER_path, sent_path, result_path):
        self.save_path = save_path
        self.load_path = load_path
        self.db_name = db_name
        self.table_name = table_name
        self.NER_path = NER_path
        self.sent_path = sent_path
        self.result_path = result_path
        self.trie = Trie(self.save_path,self.load_path, self.db_name, self.table_name)
        self.reader = None
        self.title_as_sent = TitleSent()


    def init(self):
        print("init begin:")
        print("- loading NERs...")
        NERs = LoadNERs(self.NER_path, self.sent_path, self.db_name, self.table_name)
        NERs.get_general_typelist(type1, type2)
        self.reader = NERs.Reader(-1)
        print("- done")
        print("- loading trie...")
        if not os.path.exists(self.load_path):
            self.trie.build()
        self.trie.load()
        print("- done")

    def process(self):
        with open(self.result_path,"w") as f:
            sent_id = 0
            for each in tqdm(self.reader):
                result = self.trie.search_notin(each.cui1_dic, each.cui2_dic)
                if result:
                    for pair in result:
                        cui1 = pair[0]
                        cui2 = pair[1]
                        cui1_attrs = each.cui1_dic[cui1]
                        cui2_attrs = each.cui2_dic[cui2]
                        for cui1_attr in cui1_attrs:
                            for cui2_attr in cui2_attrs:
                                item = EntityPair(each.article_id, each.sent_id, each.title, each.text, each.article_structure,\
                                     cui1, cui2, cui1_attr, cui2_attr, self.title_as_sent)
                                if item.is_entitypair:
                                    f.write(str(item))

def generateEntityPair(file_index):
    NER_file_tmp = NER_file +str(file_index)+".txt"
    sent_file_tmp = sent_file + str(file_index) + '.txt'
    output_file_tmp = output_file +str(file_index)+".txt"
    generator = GenerateEntityPair(db_name, table_name, save_path, load_path, NER_file_tmp, sent_file_tmp, output_file_tmp)
    generator.init()
    print('processing...')
    generator.process()
    print("- done")
    
if __name__ == "__main__":
    plist = []
    for i in range(num):
        p = Process(target=generateEntityPair,args = (i,))
        p.start()
        plist.append(p)
    for ap in plist:
        ap.join()

