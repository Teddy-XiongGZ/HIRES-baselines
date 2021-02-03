

def clean(old_file, new_file):
	i = 0
	cui_set_list = []
	with open(old_file)as f:
		with open(new_file, 'w')as fw:
			line = f.readline()
			while line:
				if i%100 ==0:
					print('%d done'%i)
				cui_set = set(line.split('|')[:2])
				if not cui_set in cui_set_list:
					cui_set_list.append(cui_set)
					fw.writelines(line)
				line = f.readline()
				i += 1

if __name__ == '__main__':
	ddx_positive_sample = '../data/positive_sample_ddx.txt'
	ddx_positive_sample_new = '../data/positive_sample_ddx_unique.txt'
	clean(ddx_positive_sample, ddx_positive_sample_new)
