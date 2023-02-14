#!/bin/bash

export DISPLAY=:2
bash install_env/kill.sh
python task_runner.py --config_path config.yaml




