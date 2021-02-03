#!/bin/bash

echo "diso diso"
echo "Now Negative Sample_1"
python baselines.py ../data/positive_sample_diso_diso.txt ../data/negative_sample1_diso_diso.txt CNN cnn.log -d cuda


echo "Now Negative Sample_3"
python baselines.py ../data/positive_sample_diso_diso.txt ../data/negative_sample3_diso_diso.txt CNN cnn.log -d cuda

echo "Now Negative Sample_13"
python baselines.py ../data/positive_sample_diso_diso.txt ../data/negative_sample_mixed13_diso_diso.txt CNN cnn.log -d cuda
