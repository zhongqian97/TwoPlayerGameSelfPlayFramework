#!/bin/bash

# export DISPLAY=:2
bash parallel_scripts/copy_file.sh 1>/dev/null 2>&1
bash parallel_scripts/kill.sh
read -s -n1 -p "按任意键继续 ... "

int=1
while(( $int<=3 ))
do
    echo $int
    bash install_env/kill.sh
    python train_runner.py --config_path config.yaml

    # python test_runner.py --config_path test_config.yaml
    # python test_runner_for_all_agents.py --test_selfplay true --config_path config.yaml
    bash install_env/kill.sh
    python test_runner_for_all_agents_and_all_model.py --config_path config.yaml
    let "int++"
done



