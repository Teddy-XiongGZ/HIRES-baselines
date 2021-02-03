import pickle
import re
from tqdm import tqdm
import pymysql


"""Trie结点类"""
class TrieNode:
    def __init__(self):
        self.table = dict()
        self.phrase_end = False
        self.phrase = None
        self.phrase_attr = None

    def __len__(self):
        return len(self.table)

class Trie:
    def __init__(self,save_path,load_path, db_name, table_name):
        self.root = TrieNode()
        self.save_path = save_path
        self.load_path = load_path
        self.db_name = db_name
        self.table_name = table_name

    def insertPhrase(self, phrase,phrase_attr):
        node = self.root
        words = phrase.split()

        for ch in phrase:
            if ch not in node.table:
                node.table[ch] = TrieNode()
            node = node.table[ch]

        node.phrase_end = True
        node.phrase = phrase
        node.phrase_attr = phrase_attr

    def search(self, cui1_dic, cui2_dic, start=0):
        result = []
        for cui1 in cui1_dic:
            node = self.root
            for i in range(len(cui1)):
                if cui1[i] not in node.table:
                    break
                node = node.table[cui1[i]]
            if node.phrase_end:
                for cui2 in cui2_dic:
                    if cui2 in node.phrase_attr:
                        result.append([cui1, cui2])
        return result

    def search_notin(self, cui1_dic, cui2_dic, start=0):
        result = []
        for cui1 in cui1_dic:
            node = self.root
            for i in range(len(cui1)):
                if cui1[i] not in node.table:
                    for cui2 in cui2_dic:
                        result.append([cui1, cui2])
                    break
                node = node.table[cui1[i]]
            if node.phrase_end:
                for cui2 in cui2_dic:
                    if cui2 not in node.phrase_attr:
                        result.append([cui1, cui2])
        return result

    """建Trie树"""
    def build(self):
        db = pymysql.connect(host = 'localhost', user = 'root', password = 'Verita_20sql', port=3308)
        cur = db.cursor()
        cur.execute('use %s;'%self.db_name)
        cur.execute('select distinct cui1 from %s;'%(self.table_name))
        result = cur.fetchall()
        j = 0
        for item in result:
            if j%1000 == 0:
                print('%d finished'%j)
            phrase = item[0]
            cur.execute('select cui2 from %s where cui1 = "%s";'%(self.table_name, phrase))
            tmp_result = cur.fetchall()
            phrase_attr = [i[0] for i in tmp_result]
            self.insertPhrase(phrase, phrase_attr)
            j += 1
        self.save()

    def save(self):
        print("saving")
        f = open(self.save_path,"wb")
        pickle.dump(self.root,f)
        f.close()


    def load(self):
        print("loading")
        f = open(self.load_path,"rb")
        self.root = pickle.load(f)
        f.close()

if __name__ == '__main__':
    trie = Trie('../data/trie_disodiso_reverse.pkl','../data/trie_disodiso_reverse.pkl', 'relation', 'disodiso')
    trie.build()