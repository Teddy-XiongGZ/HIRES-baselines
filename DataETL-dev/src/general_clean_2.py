from tqdm import tqdm
from LoadGeneralCleanSentence import LoadSentences, Sentence
import argparse
import random
'''
sample 1000 sentences from ep with more than 1000 sentences

'''
parser = argparse.ArgumentParser()
parser.add_argument('input_file', action='store', type=str,
                    help='The path to input sentences')

parser.add_argument('output_file', action='store', type=str,
                    help='The path to output sentences')


args = parser.parse_args()
input_file = args.input_file
output_file = args.output_file


class Cleaner2:
	def __init__(self, inpath, outpath):
		sentence_loader = LoadSentences(inpath)
		self.sentences = sentence_loader.Reader()
		self.inpath = inpath
		self.outpath = outpath
		self.dic = {}


	def process(self):
		for sentence in tqdm(self.sentences):
			cui1_cui2 = sentence.cui1 + sentence.cui2
			if len(sentence.text.split('<sep>')) > 1:
				if cui1_cui2 not in self.dic:
					self.dic[cui1_cui2] = []
				self.dic[cui1_cui2].append(str(sentence))
		with open(self.outpath, 'w') as outfile:
			c = 0
			for cui1_cui2 in tqdm(self.dic):
				num = len(self.dic[cui1_cui2])
				if num > 1000:
					c = c+1
					self.dic[cui1_cui2] = random.sample(self.dic[cui1_cui2], 1000)
				outfile.writelines(self.dic[cui1_cui2])
		print("%d entitypair re-sampled"%c)

def clean2():
	cleaner = Cleaner2(input_file, output_file)
	cleaner.process()

if __name__ == '__main__':
	clean2()
