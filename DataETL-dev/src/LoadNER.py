import pymysql

class SentNER:
	def __init__(self, sent_list, attr_list):
		self.article_id = sent_list[1]
		self.sent_id = attr_list[0]
		self.cui1_dic = attr_list[1]
		self.cui2_dic = attr_list[2]
		self.title = sent_list[2]
		self.text = sent_list[3]
		self.article_structure = sent_list[4]

	def __str__(self):   #输出字符串
		return "sent Id: " + str(self.sent_id) + "\n" + "NER cui1: " + str(self.cui1_dic) + "\n" +\
				 "NER cui2: " + str(self.cui2_dic) + "\n" + 'title: ' + str(self.title) + '\n' +\
				 'text: ' + str(self.text) + '\n' + 'article_structure: ' + str(self.article_structure)

class LoadNERs:
	def __init__(self, NER_filepath, sent_filepath, db_name, table_name):
		self.NER_filepath = NER_filepath
		self.sent_filepath = sent_filepath
		self.cui1_type = []
		self.cui2_type = []
		self.db_name = db_name
		self.table_name = table_name

	def get_cuitype_list(self):
		print('connecting mysql...')
		db = pymysql.connect(host = '127.0.0.1', user = 'root', password = '')
		cur = db.cursor()
		cur.execute('use %s;'%self.db_name)
		cur.execute('select distinct cui1_type from %s;'%self.table_name)
		result = cur.fetchall()
		cui1_type = [r[0] for r in result]
		cur.execute('select distinct cui2_type from %s;'%self.table_name)
		result = cur.fetchall()
		cui2_type = [r[0] for r in result]
		self.cui1_type = cui1_type
		self.cui2_type = cui2_type

	def get_general_typelist(self, type1, type2):
		'''
		print('connecting mysql...')
		db = pymysql.connect(host = '127.0.0.1', user = 'root', password = '')
		cur = db.cursor()
		cur.execute('use umls0;')
		cur.execute('select CUI_SEMI_TYPE from semi_groups where CUI_TYPE="%s";'%type1)
		result = cur.fetchall()
		cui1_type = [r[0] for r in result]
		cui1_type.remove('Finding')
		cur.execute('select CUI_SEMI_TYPE from semi_groups where CUI_TYPE="%s";'%type2)
		result = cur.fetchall()
		cui2_type = [r[0] for r in result]
		'''
		self.cui1_type = type1
		self.cui2_type = type2


	def Process(self, sent_id, sent, NER_cui1, NER_cui2):
		NER_cui1_dic = {}  #{CUI:[start, end, entity, cui_type,is_title]}
		NER_cui2_dic = {}
		for NER in NER_cui1:
			if NER[6] not in NER_cui1_dic:
				NER_cui1_dic[NER[6]] = []
			NER_cui1_dic[NER[6]].append(NER[3:6] + NER[7:9]) 
		for NER in NER_cui2:
			if NER[6] not in NER_cui2_dic:
				NER_cui2_dic[NER[6]] = []
			NER_cui2_dic[NER[6]].append(NER[3:6] + NER[7:9])
		sent_list = sent.split('|')
		return SentNER(sent_list, [sent_id, NER_cui1_dic, NER_cui2_dic])
		

	"""逐行读取文件并返回迭代器"""
	def Reader(self, num):
		NER_infile = open(self.NER_filepath)
		sent_infile = open(self.sent_filepath)

		i = 0
		NER_result = NER_infile.readline()
		NER_result_list = NER_result.strip().split('|')
		while NER_result.strip():
			if i ==num:
				break
			NER_cui1 = []  #[[article_id, sent_id, cui_id, start, end, entity, cui_type, is_title, is_article_structure], ...]
			NER_cui2 = []
			while NER_result_list[1] == str(i):
				if NER_result_list[-1] == '0':
					if NER_result_list[-3] in self.cui1_type:
						NER_cui1.append(NER_result_list)
					if NER_result_list[-3] in self.cui2_type:
						NER_cui2.append(NER_result_list)
				NER_result = NER_infile.readline()
				#print(NER_result)
				if not NER_result:
					break
				else:
					NER_result_list = NER_result.strip().split('|')
			sent = sent_infile.readline().lower()
			if NER_cui1 and NER_cui2:
				#print(NER_cui1)
				#print(NER_cui2)
				yield self.Process(i, sent, NER_cui1, NER_cui2)
			i += 1
		NER_infile.close()
		sent_infile.close()





def test():
	filepath = '/media/sdc/RelationExtractionModels/newdata/3-NER/src/NERresult_8.txt'
	ner_loader = LoadNERs(filepath)
	print('- loading NER...')
	ner_loader.get_cuitype_list()
	reader = ner_loader.Reader(5)
	print('- done')
	for item in reader:
		print(item)



if __name__ == '__main__':
	test()
