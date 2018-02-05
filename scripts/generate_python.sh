#!/usr/bin/env bash
assessment=$1;
cd /mnt/vol1/${assessment};
mkdir -p inputs;
for run in 1 2 3;
do 
    echo "Generating 3 inputs and outputs...";
    python3 input_generators/1/example_generator.py > inputs/${run}.txt;
    python3 model_solutions/1/example.solution.py < ${run}.txt > expected_outputs/${run}.txt;
done
