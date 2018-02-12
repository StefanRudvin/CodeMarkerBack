#!/usr/bin/env bash
filename=$1;
assessment=$2;
submissionId=$3;
cd /mnt/vol1/${assessment};
mkdir -p submissions/${submissionId}/outputs;
TIMEFORMAT='%3R'
for f in inputs/*; 
do 
    echo "Processing $f file..";
    start=$(date +%s.%N)
    python3 submissions/${submissionId}/${filename} < ${f} > submissions/${submissionId}/outputs/$(basename ${f});
    dur=$(echo "$(date +%s.%N) - $start" | bc)
    printf "%.6f" $dur > submissions/${submissionId}/outputs/t_$(basename ${f})
done
