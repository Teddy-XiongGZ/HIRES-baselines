import json
import random

class EntitypairAttr:
	def __init__(self):
		self.text = []
		self.article_structure = []
		self.pos1 = []
		self.pos2 = []
		self.num = 0

	def insert(self, attr_list):
		self.text.append(attr_list[6])
		self.article_structure.append(attr_list[7])
		self.pos1.append(eval(attr_list[8]))
		self.pos2.append(eval(attr_list[9]))
		self.num += 1

	def __str__(self):
		return json.dumps(self.text) + '|' + json.dumps(self.article_structure) + '|' + str(self.pos1) + '|' + str(self.pos2)

class LoadEntitypairs:
	def __init__(self, filepath):
		self.filepath = filepath
		self.dic = {}

	def group(self, line):
		line_list = line.split('|')
		cui1_cui2 = line_list[2]+line_list[4]
		if cui1_cui2 not in self.dic:
			self.dic[cui1_cui2] = EntitypairAttr()
		self.dic[cui1_cui2].insert(line_list)


	def loader(self):
		with open(self.filepath) as f:
			lines = f.readlines()
			for line in lines:
				self.group(line)

	def count(self):
		self.count = {}
		with open(self.filepath) as f:
			lines = f.readlines()
			for line in lines:
				line_list = line.split('|')
				cui1_cui2 = line_list[2]+line_list[4]
				if cui1_cui2 not in self.count:
					self.count[cui1_cui2] = 0
				self.count[cui1_cui2] += 1