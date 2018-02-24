#!/usr/bin/env bash
# Script responsible for generating input based on given code

# Fetch assessment ID and language of the generator
assessment=$1;
language=$2;

# Create required directories
cd /mnt/vol1/${assessment};
mkdir -p inputs;
mkdir -p expected_outputs;

# Run three times to create three instances
for run in 1 2 3;
do
    # Depending on the language use different compiler
    # First compile the file, then run it based on obtained input
    case $language in
        java)
            javac input_generators/*/*.java;
            class=$(ls input_generators/*/);
            filename=$(basename $class)
            filename="${filename%.*}"
            java -cp input_generators/* $filename &> inputs/${run}.txt;
            
            javac model_solutions/*/*.java;
            class=$(ls model_solutions/*/);
            filename=$(basename $class)
            filename="${filename%.*}"
            java -cp model_solutions/* $filename < inputs/${run}.txt &> expected_outputs/${run}.txt;
        ;;
        cpp)
            directory=$(find input_generators/* -maxdepth 0)
            g++ -o $directory/out input_generators/*/*.cpp;
            $directory/out &> inputs/${run}.txt;
            
            directory=$(find model_solutions/* -maxdepth 0)
            g++ -o $directory/out model_solutions/*/*.cpp;
            $directory/out < inputs/${run}.txt &> expected_outputs/${run}.txt;
        ;;
        c)
            directory=$(find input_generators/* -maxdepth 0)
            gcc -o $directory/out input_generators/*/*.cpp;
            $directory/out &> inputs/${run}.txt;
            
            directory=$(find model_solutions/* -maxdepth 0)
            gcc -o $directory/out model_solutions/*/*.cpp;
            $directory/out < inputs/${run}.txt &> expected_outputs/${run}.txt;
        ;;
        # All interpreted languages dont need to be compiled
        # The instruction is generic
        *)
            $language input_generators/*/* &> inputs/${run}.txt;
            $language model_solutions/*/* < inputs/${run}.txt &> expected_outputs/${run}.txt;
        ;;
    esac
    
done
