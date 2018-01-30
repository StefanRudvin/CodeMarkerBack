filename=$1;
assessment=$2;
cd /mnt/vol1;
python3 /mnt/vol1/submissions/$assessment/$filename < input.txt > output.txt;