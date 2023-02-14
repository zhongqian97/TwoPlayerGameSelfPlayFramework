num=10
cd /root/desc/pytorchselfplayframework ; export DISPLAY=:$num ; ray stop ; ray start --head

host="172.18.29.45"

cat parallel_scripts/SSH | while read line
do
    let "num++"
    echo $num
    array=(${line})
    ssh -p ${array[1]} root@${array[0]} "cd /root/desc/pytorchselfplayframework ; export DISPLAY=:"$num" ; ray stop ; ray start --address='"$host":6379' --redis-password='5241590000000000'" &
done
