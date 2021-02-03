from LoadEmbedding import LoadCuiEmbedding
from LoadEntitypairs import LoadEntitypairs
from tqdm import tqdm
import json
import os
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('input_file', action='store', type=str,
                    help='The path to input sentences')

parser.add_argument('output_file', action='store', type=str,
                    help='The path to output sentences')

parser.add_argument('embed_path', action='store', type=str,
                    help='The path to load embedding')

parser.add_argument('label', action='store', type=int,
                    help='1 for positive, 0 for negative')
parser.add_argument('sample_type', action='store', type=int, 
help='0 for positive, num greater than 0 indicates negative smaple type')

args = parser.parse_args()
load_path = args.input_file
save_path = args.output_file
embed_path = args.embed_path
label = args.label
sample_type = args.sample_type

class EmbeddingMatch:
    def __init__(self, load_path, save_path, embed_path):
        self.load_path = load_path
        self.save_path = save_path
        self.embed_path = embed_path

    def init(self):
        entitypair_loader = LoadEntitypairs(self.load_path)
        print('- loading entitypairs...')
        entitypair_loader.loader()
        self.grouped_pairs = entitypair_loader.dic
        print('- done')
        self.embed_loader = LoadCuiEmbedding(self.embed_path)
        print('- loading cui embeddings...')
        if not os.path.exists(self.embed_path):
            print('building...')
            self.embed_loader.build()
        self.embed_loader.load()
        print('- done')


    def process(self):
        with open(self.save_path, 'w') as f:
            for cui1_cui2 in tqdm(self.grouped_pairs):
                split = int(len(cui1_cui2)/2)
                cui1 = cui1_cui2[:split]
                cui2 = cui1_cui2[split:]
                embed1 = self.embed_loader.get_embed(cui1)
                embed2 = self.embed_loader.get_embed(cui2)
                f.writelines('|'.join([cui1, cui2, str(self.grouped_pairs[cui1_cui2]), embed1, embed2, str(label),str(sample_type)])+'\n')


def generate_positive_sample():
    generator = EmbeddingMatch(load_path, save_path, embed_path)
    generator.init()
    generator.process()

if __name__ == '__main__':
    generate_positive_sample()
