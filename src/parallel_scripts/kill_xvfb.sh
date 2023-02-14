pkill -9 Xvfb &
cat parallel_scripts/SSH | while read line
do
    echo $line
    array=(${line})
    ssh -p ${array[1]} root@${array[0]} "pkill -9 Xvfb" &
done
