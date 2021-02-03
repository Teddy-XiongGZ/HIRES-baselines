from LoadGeneralCleanSentence import LoadSentences, Sentence 
from tqdm import tqdm
#adjust order of ep
class Reverse:
	def __init__(self, old_file, new_file):
		self.new_file = new_file
		self.sentence_reader = LoadSentences(old_file).Reader()

	def process(self):
		with open(self.new_file, 'w')as fw:
			for sentence in tqdm(self.sentence_reader):
				cui1_pos = sentence.pos1.index(0)
				cui2_pos = sentence.pos2.index(0)
				try:
					assert not cui1_pos == cui2_pos
				except:
					print(sentence.article_id+'|'+sentence.sent_id)
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

if __name__ == '__main__':
	old_file = '../data/general_clean_diso_diso_1.txt'
	new_file = '../data/general_clean_diso_diso_2.txt'
	cleaner = Reverse(old_file, new_file)
	cleaner.process()
