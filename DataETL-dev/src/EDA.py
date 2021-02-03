from LoadGeneralCleanSentence import LoadSentences, Sentence
from tqdm import tqdm
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('sent_path', action='store', type=str,
                    help='The path to input file')

parser.add_argument('sample_path', action='store', type=str,
                     help='The path to input final sample')
parser.add_argument('len_except_path', action='store', type=str,
                    help='The path to input length exception')

parser.add_argument('eda_path', action='store', type=str,
                    help='The path to output eda result')

args = parser.parse_args()
sent_path = args.sent_path
sample_path = args.sample_path
len_except_path = args.len_except_path
eda_path = args.eda_path

class EDA:
	def __init__(self, sent_path, pos_sample_path, len_except_path, eda_path):
		self.sentence_loader = LoadSentences(sent_path)
		self.sentences = self.sentence_loader.Reader()
		self.pos_sample_path = pos_sample_path
		self.len_except_path = len_except_path
		self.sent_cnt = 0
		self.sent_word_cnt = []
		self.both_entities_in_sent_cnt = 0
		self.entity_in_title_cnt = 0
		self.header_word_cnt = []
		self.empty_title_cnt = 0
		self.empty_header_cnt = 0 
		self.entity_pairs_cnt = 0
		self.entity_pairs_sent_cnt = []
		self.sent_length_filtered_cnt = 0
		self.pos1_max = 0
		self.pos2_max = 0
		self.eda_path = eda_path

	def process(self):
		for s in tqdm(self.sentences):
			self.sent_cnt += 1
			self.sent_word_cnt.append(s.text_length)
			if s.is_title1 or s.is_title2:
				self.entity_in_title_cnt += 1
			else:
				self.both_entities_in_sent_cnt += 1
			if s.text.startswith('<empty_title>'):
				self.empty_title_cnt += 1

			header = s.article_structure.replace('.', ' ').strip()
			self.header_word_cnt.append(len(header.split()))
			if not header:
				self.empty_header_cnt += 1
			self.pos1_max = max(self.pos1_max, s.pos1[0], s.pos1[-1])
			self.pos2_max = max(self.pos2_max, s.pos2[0], s.pos2[-1])

		if self.pos_sample_path is not None:
			with open(self.pos_sample_path) as f:
				lines = f.readlines()
				for line in lines:
					line = line.split('|')
					self.entity_pairs_cnt += 1
					try:
						self.entity_pairs_sent_cnt.append(len(eval(line[2])))
					except:
						print(line)


		with open(self.len_except_path) as f:
			lines = f.readlines()
			self.sent_length_filtered_cnt = len(lines)


	def dump(self):
		dic = 	{'sent_cnt' :self.sent_cnt,\
				'sent_word_cnt' :self.sent_word_cnt,\
				'both_entities_in_sent_cnt' :self.both_entities_in_sent_cnt,\
				'entity_in_title_cnt' :self.entity_in_title_cnt,\
				'header_word_cnt' :self.header_word_cnt,\
				'empty_title_cnt' :self.empty_title_cnt,\
				'empty_header_cnt' :self.empty_header_cnt,\
				'entity_pairs_cnt' :self.entity_pairs_cnt,\
				'entity_pairs_sent_cnt' :self.entity_pairs_sent_cnt,\
				'sent_length_filtered_cnt' :self.sent_length_filtered_cnt,\
				'pos1_max' :self.pos1_max,\
				'pos2_max' :self.pos2_max}
		with open(eda_path, 'w') as fw:
			json.dump(dic, fw)

def eda():
	eda = EDA(sent_path, sample_path, len_except_path, eda_path)
	eda.process()
	eda.dump()

if __name__ == '__main__':
	eda()
