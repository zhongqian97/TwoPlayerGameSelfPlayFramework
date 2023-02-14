#!/bin/bash

int=1
debug=1
if [[ $debug>0 ]];then
    epoch=1
else
    epoch=20
fi

while(( $int<=$epoch ))
do
    echo $int
    bash parallel_scripts/clean.sh 1>/dev/null 2>&1
    bash parallel_scripts/copy_file.sh 1>/dev/null 2>&1
    bash parallel_scripts/kill.sh
    if [[ $debug>0 ]];then
        read -s -n1 -p "等到所有服务器Done后，再按任意键继续 ... "
    else
        echo "自动运行中 ... "
        sleep 600
    fi
    python task_runner.py --config_path config.yaml
    let "int++"
done





