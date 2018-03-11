#!/usr/bin/env bash
# Run given file in Docker container using given compiler
# Creation date 2018-03-04 by Konrad Dryja

# First access all parameters passed through commandline
filename=$1;
assessment=$2;
submissionId=$3;
num=$4;
language=$5;

# Change current directory to where the considered assessment is
cd "/mnt/vol1/${assessment}" || return;
# Create directory for outputs
mkdir -p "submissions/${submissionId}/static_outputs";
# Iterate over every input in the inputs folder
for f in static_inputs/*;
do
    echo "Processing $f file..";
    # Take note of the starting time to measure execution time
    start=$(date +%s.%N)
    output=$(basename "${f}")
    
    # Depending on the language we will run different compiler / interpreter
    # You redirect input to the file and save output in the outputs folder in all the cases.
    case $language in
        java)
            javac "submissions/${submissionId}/${filename}";
            java -cp submissions/${submissionId} ${filename%.*} < "${f}" &> "submissions/${submissionId}/static_outputs/${output}";
        ;;
        cpp)
            g++ -o "submissions/${submissionId}/out" "submissions/${submissionId}/${filename}";
            "submissions/${submissionId}/out" < "${f}" &> "submissions/${submissionId}/static_outputs/${output}";
        ;;
        c)
            gcc -o "submissions/${submissionId}/out" "submissions/${submissionId}/${filename}";
            "submissions/${submissionId}/out" < "${f}" &> "submissions/${submissionId}/static_outputs/${output}";
        ;;
        *)
            ${language} "submissions/${submissionId}/${filename}" < "${f}" &> "submissions/${submissionId}/static_outputs/${output}";
        ;;
    esac
    
    # Finally check how long the execution took and save the results in a separate file
    dur=$(echo "$(date +%s.%N) - $start" | bc)
    printf "%.6f" "$dur" > "submissions/${submissionId}/static_outputs/t_${output}";
done
