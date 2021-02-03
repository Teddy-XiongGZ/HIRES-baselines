# %%
import pandas as pd 
file = '../data/disodiso500gold.txt'
df = pd.read_csv(file, sep='|')
label_dic = {'DDx':'1', 'May Be Caused By':'3', 'May Cause':'2', 'Others':'0'}
gold_sample = {}
for item in df.iterrows():
    gold_sample[item[1]['cui1']+item[1]['cui2']] = label_dic[item[1]['Anotated_Final Label']]
# %%
print(len(gold_sample))
# %%
infile = '../data/positive_sample_diso_diso.txt'
outfile = '../data/gold_sample_disodiso_500.txt'
gold_lines = []
with open(infile)as f:
    line = f.readline()
    while line:
        line_list = line.strip().split('|')
        try:
            assert len(line_list) == 10
        except:
            print(len(line_list))
        pair = line_list[0]+line_list[1]
        if pair in gold_sample:
            line_list[8] = gold_sample[pair]
            gold_lines.append('|'.join(line_list)+'\n')
        line = f.readline()
with open(outfile, 'w')as fw:
    fw.writelines(gold_lines)

# %%
