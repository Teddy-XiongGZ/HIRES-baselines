from lib.LoadSentence import LoadSentences
from lib.Trie import Trie,TrieNode,TrieMatchResult
from lib.Orm import NER,NER_ORM
from tqdm import tqdm
from multiprocessing import Process

class NERresult:
    def __init__(self,art_id,sen_id,NER_id,trie_match_result,is_title,is_structure):
        self.article_id = art_id
        self.sen_id = sen_id
        self.NER_id = NER_id
        self.begin = trie_match_result.begin
        self.end = trie_match_result.end
        self.term = trie_match_result.phrase
        self.cui = trie_match_result.phrase_attr[0]
        self.cui_type = trie_match_result.phrase_attr[1]
        self.is_title = is_title
        self.is_structure = is_structure

    def __str__(self):
        return str(self.article_id)+'|'+str(self.sen_id)+'|'+str(self.NER_id)+'|'+str(self.begin)+\
            '|'+str(self.end)+'|'+str(self.term)+'|'+str(self.cui)+'|'+str(self.cui_type)+'|'\
            +str(self.is_title)+'|'+str(self.is_structure)  +'\n'

    def tolist(self):
        return[self.article_id,self.sen_id,self.NER_id,self.begin,self.end,self.term,\
                self.cui,self.cui_type,self.is_title,self.is_structure]


class GenerateNER:
    def __init__(self,sentences_path,result_path,orm_flag=0):
        self.phrase_set_path = "src/terms.pkl"
        self.save_path = "src/trie.pkl"
        self.load_path = "src/trie.pkl"
        self.sentences_num = -1
        self.sentences_path = sentences_path
        self.result_path = result_path
        self.trie = Trie(self.phrase_set_path,self.save_path,self.load_path)
        self.reader = None
        self.orm_flag = orm_flag
        if self.orm_flag:
            self.ner_orm = NER_ORM(None)
            

    def init(self):
        print("init begin:")
        print("- loading sentences...")
        sentences = LoadSentences(self.sentences_path,self.sentences_num)
        print("- done")
        self.reader = sentences.Reader()
        print("- loading trie...")
        self.trie.load()
        print("- done")
        return 

    def process(self):
        with open(self.result_path,"w") as f:
            sent_id = 0
            for each in tqdm(self.reader):

                result = self.trie.match(each.title)
                if result:
                    for NER_id in range(len(result)):
                       res_item = NERresult(each.article_id,sent_id,NER_id,result[NER_id],1,0)
                       if self.orm_flag:
                            self.ner_orm.Insert(res_item.tolist())
                       f.write(str(res_item))

                result = self.trie.match(each.sentence)
                if result:
                    for NER_id in range(len(result)):
                       res_item = NERresult(each.article_id,sent_id,NER_id,result[NER_id],0,0)
                       if self.orm_flag:
                            self.ner_orm.Insert(res_item.tolist())
                       f.write(str(res_item))

                result = self.trie.match(each.article_structure)
                if result:
                    for NER_id in range(len(result)):
                       res_item = NERresult(each.article_id,sent_id,NER_id,result[NER_id],0,1)
                       if self.orm_flag:
                            self.ner_orm.Insert(res_item.tolist())
                       f.write(str(res_item))

                sent_id += 1
        print("done")
        return 

def generateNER(file_index):
    input_file = "../2-SentenceSplit/sent_all_"+str(file_index)+".txt"
    output_file = "src/NERresult_"+str(file_index)+".txt"
    generator = GenerateNER(input_file,output_file)
    generator.init()
    generator.process()
    
if __name__ == "__main__":
    plist = []
    for i in range(4,9):
        p = Process(target=generateNER,args = (i,))
        p.start()
    for ap in plist:
        ap.join()
