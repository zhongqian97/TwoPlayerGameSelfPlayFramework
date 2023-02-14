cd /root/desc/pytorchselfplayframework ; bash ./install_env/install_env_py.sh &

cat parallel_scripts/SSH | while read line
do
    echo $line
    array=(${line})
    ssh -p ${array[1]} root@${array[0]} "cd /root/desc/pytorchselfplayframework ; bash ./install_env/install_env_py.sh" &
done