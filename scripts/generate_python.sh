#!/usr/bin/env bash
assessment=$1;
cd /mnt/vol1/${assessment};
mkdir -p inputs;
mkdir -p expected_outputs;
for run in 1 2 3;
do
    python3 input_generators/*/*.py > inputs/${run}.txt;
    python3 model_solutions/*/*.py < inputs/${run}.txt > expected_outputs/${run}.txt;
done
