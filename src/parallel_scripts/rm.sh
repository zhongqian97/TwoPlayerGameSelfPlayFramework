# cd /root/desc/pytorchselfplayframework ; bash ./temp/kill.sh &
cat parallel_scripts/SSH | while read line
do
    echo $line
    array=(${line})
    ssh -p ${array[1]} root@${array[0]} "cd /root/desc/pytorchselfplayframework ; rm -rf checkpoints temp" &
done
