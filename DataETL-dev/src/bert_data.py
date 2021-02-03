import data_path
import os
import numpy as np
import json

class BertTextLoader(object):

    def __init__(self, 
                data_path, 
                use_title = False):
        self.data_path = data_path
        self.use_title = use_title
        self.lines = []

    def __iter__(self):
        self.idx = 0
        return self

    def __len__(self):
        return len(self.lines)

    def __next__(self):
        if self.idx < self.__len__():
            line = self.lines[self.idx]
            all_text = line.split('|')[2]
            text_list = json.loads(all_text)
            sentences = []
            for text in text_list:
                try:
                    text_split = text.split('<sep>')
                    title, main_body = text_split[0].strip(), text_split[1].strip()
                except:
                    raise Exception("Text failed to be splited by . {}".format(text_split))
                result = ""
                if self.use_title:
                    result = ' ||| '.join([title, main_body])
                else:
                    result = main_body
                sentences.append(result)
            self.idx += 1
            return sentences
        raise StopIteration

    def __getitem__(self, idx):
        return self.lines[idx].split('|')[4]

    def load(self):
        print("BertTextLoader reading from {}".format(self.data_path))
        f = open(self.data_path, 'r')
        self.lines = f.readlines()
        f.close()

def test():
    path = os.path.join(data_path.DATA_PATH, "positive_sample_2.txt")
    loader = BertTextLoader(path, use_title=True)
    loader.load()
    for sentences in loader:
        print(len(sentences))

if __name__ == '__main__':
    test()
