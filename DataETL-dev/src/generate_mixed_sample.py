import random
import argparse
from random import sample


def read_sample(path):
    lines = []
    with open(path, 'r') as file:
        while True:
            line = file.readline()
            if not line:
                break
            lines.append(line)
    return lines


def generate_mixed_sample(ratio, out_path, sample_num):   #example: 1:1:1/2:0:1

    random.seed(0)
    ratio = ratio.split(":")
    ratio = [int(x) for x in ratio]
    ratio_1 = ratio[0]/(ratio[0]+ratio[1]+ratio[2])
    ratio_2 = ratio[1] / (ratio[0] + ratio[1] + ratio[2])
    ratio_3 = ratio[2] / (ratio[0] + ratio[1] + ratio[2])

    neg_1 = read_sample("../data/negative_sample1_diso_diso.txt")
    neg_2 = read_sample("../data/negative_sample2_diso_diso.txt")
    neg_3 = read_sample("../data/negative_sample3_diso_diso.txt")

    neg_1 = sample(neg_1, int(ratio_1*sample_num))
    neg_2 = sample(neg_2, int(ratio_2*sample_num))
    neg_3 = sample(neg_3, int(ratio_3*sample_num))
    mixed_sample = neg_1 + neg_2 + neg_3
    random.shuffle(mixed_sample)

    with open(out_path, 'w') as file:
        print("print")
        for sample_ in mixed_sample:
            file.write(sample_)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("ratio", type=str)
    parser.add_argument("out_path", type=str)
    parser.add_argument("-n", "--sample_number", type=int, default=5000)
    args = parser.parse_args()

    generate_mixed_sample(args.ratio, args.out_path, args.sample_number)