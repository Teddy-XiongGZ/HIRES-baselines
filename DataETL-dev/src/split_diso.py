#this program splits the diso-diso further clean data into three files, each is one relation
# 1. build a proper ep list for each relation
# 2. split the file according to the list
from LoadGeneralCleanSentence import LoadSentences, Sentence 
from tqdm import tqdm

class Splitter:
	def __init__(self, ep_file_list, data_file, ddx_file, mc_file, mbc_file):
		self.ep_file_list = ep_file_list
		self.sentence_loader = LoadSentences(data_file).Reader()
		self.ddx_file = ddx_file 
		self.mc_file = mc_file
		self.mbc_file = mbc_file
		self.ddx_ep = []
		self.mc_ep = []
		self.mbc_ep = []
		self.deleted_ep_set = []
		self.same_cui_cnt = 0

	def process(self, line):
		line = line.split('|')
		cui1 = line[1].strip()
		cui2 = line[4].strip()
		cuiset = {cui1, cui2}
		cuipair = cui1+cui2
		cuipair_reversed = cui2+cui1
		relation = line[2].strip()
		if cui1 == cui2:
			self.same_cui_cnt += 1
			return (cuipair, cuipair_reversed, 0)
		if relation == 'r':
			return (cuipair, cuipair_reversed, 0)
		elif relation == 'May Cause':
			flag = 2
			if cuiset in self.deleted_ep_set:
				flag = 0
			else:
				if cuipair in self.mc_ep:
					assert cuipair_reversed in self.mbc_ep
					flag = 0
				elif cuipair_reversed in self.mc_ep:
					self.mc_ep.remove(cuipair_reversed)
					self.mbc_ep.remove(cuipair)
					self.deleted_ep_set.append(cuiset)
					flag = 0
				elif cuipair in self.ddx_ep:
					self.ddx_ep.remove(cuipair)
					self.ddx_ep.remove(cuipair_reversed)
					self.deleted_ep_set.append(cuiset)
					flag = 0
			return (cuipair, cuipair_reversed, flag)
		elif relation == 'May Be Caused By':
			flag = 3
			if cuiset in self.deleted_ep_set:
				flag = 0
			else:
				if cuipair in self.mbc_ep:
					assert cuipair_reversed in self.mc_ep
					flag = 0
				elif cuipair_reversed in self.mbc_ep:
					self.mbc_ep.remove(cuipair_reversed)
					self.mc_ep.remove(cuipair)
					self.deleted_ep_set.append(cuiset)
					flag = 0
				elif cuipair in self.ddx_ep:
					self.ddx_ep.remove(cuipair)
					self.ddx_ep.remove(cuipair_reversed)
					self.deleted_ep_set.append(cuiset)
					flag = 0
			return (cuipair, cuipair_reversed, flag)
		elif relation == 'DDx':
			flag = 1
			if cuiset in self.deleted_ep_set:
				flag = 0
			else:
				if cuipair in self.ddx_ep:
					assert cuipair_reversed in self.ddx_ep
					flag = 0
				if cuipair in self.mc_ep:
					self.mc_ep.remove(cuipair)
					self.mbc_ep.remove(cuipair_reversed)
					self.deleted_ep_set.append(cuiset)
					flag = 0
				elif cuipair in self.mbc_ep:
					self.mbc_ep.remove(cuipair)
					self.mc_ep.remove(cuipair_reversed)
					self.deleted_ep_set.append(cuiset)
					flag = 0
			return (cuipair, cuipair_reversed, flag)
		else:
			print(line)
			return (cuipair, cuipair_reversed, 0)


	def build_list(self):
		for file in self.ep_file_list:
			with open(file)as f:
				line = f.readline()
				while line:
					cuipair, cuipair_reversed, flag = self.process(line)
					if flag == 0:
						pass
					elif flag == 1:
						self.ddx_ep.append(cuipair)
						self.ddx_ep.append(cuipair_reversed)
					elif flag == 2:
						self.mc_ep.append(cuipair)
						self.mbc_ep.append(cuipair_reversed)
					elif flag == 3:
						self.mbc_ep.append(cuipair)
						self.mc_ep.append(cuipair_reversed)
					line = f.readline()
		assert len(self.mc_ep) == len(self.mbc_ep)
		assert not set(self.mc_ep).intersection(set(self.mbc_ep))
		assert len(self.mc_ep+self.mbc_ep+self.ddx_ep) \
				== len(list(set(self.mc_ep+self.mbc_ep+self.ddx_ep)))

	def build_dic(self):
		self.cuipair_dic = {}
		for cuipair in self.ddx_ep:
			self.cuipair_dic[cuipair] = 1
		for cuipair in self.mc_ep:
			self.cuipair_dic[cuipair] = 2
		for cuipair in self.mbc_ep:
			self.cuipair_dic[cuipair] = 3

	def split(self):
		cnt = 0
		with open(self.ddx_file, 'w')as fddx, open(self.mc_file, 'w')as fmc, \
			open(self.mbc_file, 'w')as fmbc:
			for sentence in tqdm(self.sentence_loader):
				cuipair = sentence.cui1+sentence.cui2
				flag = self.cuipair_dic.get(cuipair, 0)
				if flag == 1:
					fddx.writelines(str(sentence))
				elif flag == 2:
					fmc.writelines(str(sentence))
				elif flag == 3:
					fmbc.writelines(str(sentence))
				else:
					cnt += 1
		print('altogether %d sentences dropped'%cnt)
		print('altogether %d cuipair with same cui removed'%self.same_cui_cnt)

if __name__ == '__main__':
	ep_file_list = ['../data/ddx_medscape.txt', '../data/may_medscape.txt', '../data/may_dDB.txt']
	data_file = '../data/further_clean_diso_diso.txt'
	ddx_file = '../data/further_clean_ddx.txt'
	mc_file = '../data/further_clean_mc.txt'
	mbc_file = '../data/further_clean_mbc.txt'
	splitter = Splitter(ep_file_list, data_file, ddx_file, mc_file, mbc_file)
	splitter.build_list()
	splitter.build_dic()
	splitter.split()




