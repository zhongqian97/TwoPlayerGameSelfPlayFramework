cat parallel_scripts/SSH | while read line
do
    echo $line
    array=(${line})
    ssh -o StrictHostKeyChecking=no -p ${array[1]} root@${array[0]} "pwd" &
done