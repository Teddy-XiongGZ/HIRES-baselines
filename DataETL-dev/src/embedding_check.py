# %%
import pickle
disodiso_pos_file = '../data/positive_sample_diso_diso.txt'
disodiso_neg1_file = '../data/negative_sample1_diso_diso.txt'
disodiso_neg2_file = '../data/negative_sample3_diso_diso.txt'
disoanat_pos_file = '../data/positive_sample_2.txt'
disoanat_neg1_file = '../data/negative_sample1.txt'
disoanat_neg2_file = '../data/negative_sample3.txt'
cui2term_file = '/media/sda1/ChenYulin/cleanterms/cui2preferredterm.pkl'
embed_dic = '../data/embed_dic.pkl'
# %%
with open(embed_dic, 'rb')as f:
    embed_dic = pickle.load(f)
# %%
def uniquefy(list1):
    return list(set(list1))
def get_unique_embedding(filepath):
    diso_cui = []
    anat_cui = []
    diso_embed = []
    anat_embed = []
    diso_empty = []
    anat_empty = []
    line_empty_cuis = []
    with open(filepath) as f:
        lines = f.readlines()
    total = len(lines)
    for line in lines:
        line_list = line.split('|')
        if line_list[0] in embed_dic:
            diso_embed.append(embed_dic[line_list[0]])
        else:
            diso_empty.append(line_list[0])
            line_empty_cuis.append(line)
        diso_cui.append(line_list[0])
        if line_list[1] in embed_dic:
            anat_embed.append(embed_dic[line_list[1]])
        else:
            anat_empty.append(line_list[1])
            line_empty_cuis.append(line)
        anat_cui.append(line_list[1])
    print(len(diso_empty))
    print(len(anat_empty))
    print(len(uniquefy(line_empty_cuis)))
    print(total)
    return uniquefy(diso_cui), uniquefy(diso_embed), uniquefy(diso_empty), uniquefy(anat_cui), uniquefy(anat_embed), uniquefy(anat_empty)
# %%
diso_pos_cui, diso_pos_embed, diso_pos_empty, anat_pos_cui, anat_pos_embed, anat_pos_empty = get_unique_embedding(disoanat_pos_file)
# %%
print(len(diso_pos_cui))
print(len(diso_pos_embed))
print(len(diso_pos_empty))
print(len(anat_pos_cui))
print(len(anat_pos_embed))
print(len(anat_pos_empty))
# %%
diso_neg1_cui, diso_neg1_embed, diso_neg1_empty, anat_neg1_cui, anat_neg1_embed, anat_neg1_empty = get_unique_embedding(disoanat_neg1_file)
# %%
print(len(diso_neg1_cui))
print(len(diso_neg1_embed))
print(len(diso_neg1_empty))
print(len(anat_neg1_cui))
print(len(anat_neg1_embed))
print(len(anat_neg1_empty))
# %%
diso_neg2_cui, diso_neg2_embed, diso_neg2_empty, anat_neg2_cui, anat_neg2_embed, anat_neg2_empty = get_unique_embedding(disoanat_neg2_file)
# %%
print(len(diso_neg2_cui))
print(len(diso_neg2_embed))
print(len(diso_neg2_empty))
print(len(anat_neg2_cui))
print(len(anat_neg2_embed))
print(len(anat_neg2_empty))
# %%
