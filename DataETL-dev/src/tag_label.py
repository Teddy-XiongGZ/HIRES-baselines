import json
from read_sentence import sentence

with open("../data/ep_label_dict.json", 'r') as f:
    eps_label_dict = json.load(f)

sents_cause = []
sents_caused = []
sents_ddx = []

with open("../data/further_clean_diso_diso.txt", encoding='utf-8') as f:
    while True:
        line = f.readline()
        if not line:
            break
        parts = line.rstrip('\n').split('|')
        sent = sentence(parts)
        eps = sent.get_eps()
        label = eps_label_dict[eps]

        if label==1:
            sents_cause.append(str(sent))
        elif label==2:
            sents_caused.append(str(sent))
        elif label==3:
            sents_ddx.append(str(sent))
        else:
            assert(0==1)
        
with open("../data/diso_diso_cause.txt", 'w', encoding='utf-8') as f:
    for sent in sents_cause:
        f.write(str(sent))

with open("../data/diso_diso_caused.txt", 'w', encoding='utf-8') as f:
    for sent in sents_caused:
        f.write(str(sent))

with open("../data/diso_diso_ddx.txt", 'w', encoding='utf-8') as f:
    for sent in sents_ddx:
        f.write(str(sent))
