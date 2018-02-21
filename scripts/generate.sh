#!/usr/bin/env bash
assessment=$1;
language=$2;
cd /mnt/vol1/${assessment};
mkdir -p inputs;
mkdir -p expected_outputs;
for run in 1 2 3;
do
    case $language in
        Python3)
            python3 input_generators/*/*.py > inputs/${run}.txt;
            python3 model_solutions/*/*.py < inputs/${run}.txt > expected_outputs/${run}.txt;
        ;;
        Python2)
            python2 input_generators/*/*.py > inputs/${run}.txt;
            python2 model_solutions/*/*.py < inputs/${run}.txt > expected_outputs/${run}.txt;
        ;;
        Ruby)
            ruby input_generators/*/*.rb > inputs/${run}.txt;
            ruby model_solutions/*/*.rb < inputs/${run}.txt > expected_outputs/${run}.txt;
        ;;
        # java)
        #     javac input_generators/*/*.java
        #     java -cp "submissions/${submissionId} ${filename%.*}" < "${f}" &> "submissions/${submissionId}/outputs/${output}";
        # ;;
    esac
    
done
