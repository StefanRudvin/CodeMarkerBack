filename=$1;
assessment=$2;
submissionId=$3;
cd /mnt/vol1/$assessment;
mkdir submissions/$submissionId/outputs;
for f in inputs/*; 
do 
    echo "Processing $f file..";
    python3 submissions/$submissionId/$filename < $f > submissions/$submissionId/outputs/$(basename $f);
done
