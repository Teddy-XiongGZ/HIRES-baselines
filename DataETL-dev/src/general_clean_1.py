from LoadSentence import LoadSentences, Sentence
from LoadTypelist import LoadTypelist
from tqdm import tqdm
import json
import argparse
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
	def __init__(self, sentence_path, type_path, save_path, exception_path):
		self.sentence_path = sentence_path
		self.type_path = type_path
		self.save_path = save_path
		self.exception_path = exception_path
		self.sentence_list = []

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
					if sentence.is_proper_sentence:
						if sentence.entity_in_sent:
							mask1 = self.type_dic[sentence.type1]
							mask2 = self.type_dic[sentence.type2]
							sentence.mask([mask1, mask2])
							sentence.calculate_pos()
							outfile.writelines(str(sentence))
					else:
						exception_file.writelines(sentence.text+'\n')

def GeneralClean():

	cleaner = Cleaner(sentence_path, type_path, save_path, exception_path)
	cleaner.init()
	cleaner.Process()

if __name__ == '__main__':
	GeneralClean()



		
