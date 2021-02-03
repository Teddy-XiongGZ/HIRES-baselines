from tqdm import tqdm
import random



class LoadItem:
	def __init__(self, infile):
		self.infile = infile

	def reader(self, n):
		f = open(self.infile, encoding='utf-8')
		line = f.readline()
		num = 0
		while line:
			num += 1
			yield line
			line = f.readline()
			if num == n:
				break
		f.close()

class Sampler:
	def __init__(self, infile, cui_term_file, outfile):
		self.ep_reader = LoadItem(infile).reader(-1)
		self.term_reader = LoadItem(cui_term_file).reader(-1)
		self.outfile = outfile
		self.cuipair_dic ={}
		self.cuiterm_dic = {}

	def init(self):
		print('loading cui pairs...')
		self.load_cuipairs()
		print('loading terms...')
		self.load_terms()

	def load_cuipairs(self):
		for line in tqdm(self.ep_reader):
			line_list = line.split('|')
			cui1 = line_list[0]
			cui2 = line_list[1]
			if cui1 not in self.cuipair_dic:
				self.cuipair_dic[cui1] = []
			self.cuipair_dic[cui1].append(cui2)

	def load_terms(self):
		for line in tqdm(self.term_reader):
			line_list = line.split('|')
			cui = line_list[1]
			term = line_list[0]
			if cui not in self.cuiterm_dic:
				self.cuiterm_dic[cui] = []
			self.cuiterm_dic[cui].append(term)

	def sample(self):
		sample = random.sample(self.cuipair_dic.items(), 200)
		cnt = 0
		sample_new = []
		for s in sample:
			cnt += len(s[1])
			if cnt < 250:
				sample_new.append(s)
			elif cnt > 250:
				cnt -= len(s[1])
				tmp_s = list(s)
				tmp_s[1] = tmp_s[1][:250-cnt]
				sample_new.append(tmp_s)
				cnt = 250
			else:
				break
		if cnt < 250:
			print('ERROR:we need more cui candidate!')
		self.sample = sample_new

	def output(self):
		with open(outfile,'w') as fw:
			for s in self.sample:
				cui1 = s[0]
				term1 = '|'.join(self.cuiterm_dic[cui1])
				for cui2 in s[1]:
					term2 = '|'.join(self.cuiterm_dic[cui2])
					fw.writelines(','.join([cui1, term1, cui2, term2])+'\n')



if __name__ == '__main__':
	infile = '../data/pred_sample.txt'
	cui_term_file = '../data/A0004cleanterms2.txt'
	outfile = '../data/pred_sample_select.csv'
	sampler = Sampler(infile, cui_term_file, outfile)
	sampler.init()
	sampler.sample()
	sampler.output()
