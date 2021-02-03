from LoadGeneralCleanSentence import LoadSentences, Sentence 
from tqdm import tqdm
from multiprocessing import Process
#adjust order of ep
'''
adjust sentence with correct ep order
delete sentence with cui1 == cui2
'''
class Reverse:
    def __init__(self, old_file, new_file):
        self.new_file = new_file
        self.sentence_reader = LoadSentences(old_file).Reader()

    def process(self):
        with open(self.new_file, 'w')as fw:
            for sentence in tqdm(self.sentence_reader):
                cui1_pos = sentence.pos1.index(0)
                cui2_pos = sentence.pos2.index(0)
                '''
                try:
                    assert not cui1_pos == cui2_pos
                except:
                    print(sentence.article_id+'|'+sentence.sent_id)
                
                if sentence.cui1!=sentence.cui2:
                    try:
                        if cui1_pos > cui2_pos:
                            text_segment = sentence.text.split()
                            text_segment[cui1_pos], text_segment[cui2_pos] = text_segment[cui2_pos], text_segment[cui1_pos]
                            sentence.cui1, sentence.cui2 = sentence.cui2, sentence.cui1
                            sentence.type1, sentence.type2 = sentence.type2, sentence.type1
                            sentence.pos1, sentence.pos2 = sentence.pos2, sentence.pos1
                            sentence.text = ' '.join(text_segment)
                        assert sentence.pos1.index(0) < sentence.pos2.index(0)
                    except:
                        print(text_segment)
                        print(len(text_segment))
                        print(sentence.article_id+'|'+sentence.sent_id)
                    fw.writelines(str(sentence))
                '''
                if sentence.cui1!=sentence.cui2 and cui1_pos < cui2_pos:
                    fw.writelines(str(sentence))

old_file = '../data/general_clean_disodiso_pred_'
new_file = '../data/general_clean_disodiso_pred_2_'
def reverse(index):
    cleaner = Reverse(old_file+str(index)+'.txt', new_file+str(index)+'.txt')
    cleaner.process()

if __name__ == '__main__':
    
    plist = []
    for i in range(9):
        p = Process(target=reverse,args = (i,))
        p.start()
        plist.append(p)
    for ap in plist:
        ap.join()
    
