num=10
Xvfb :$num -screen 0 1024x768x16 &
disown %1

cat parallel_scripts/SSH | while read line
do
    let "num++"
    echo $num
    array=(${line})
    ssh -p ${array[1]} root@${array[0]} "Xvfb :"$num" -screen 0 1024x768x16 & disown %1" &
done