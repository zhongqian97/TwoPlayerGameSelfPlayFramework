cat parallel_scripts/SSH | while read line
do
    echo $line
    array=(${line})
    rsync -av --exclude 'log' --exclude 'checkpoints' --exclude 'temp'  --exclude '.git'  --delete -e 'ssh -p '${array[1]} ../pytorchselfplayframework root@${array[0]}:/root/desc/ &
done