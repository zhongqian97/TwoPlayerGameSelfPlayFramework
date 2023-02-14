import os, math
import re
import numpy as np
import argparse
from typing import Set, Dict, Any, TextIO
import os
from pip import main
import yaml

def load_config(config_path: str, args: dict) -> Dict[str, Any]:
    try:
        with open(config_path) as data_file:
            d = _load_config(data_file)
            for k in d.keys():
                args[k] = d[k]
            return args
    except OSError:
        abs_path = os.path.abspath(config_path)
        raise Exception(f"Config file could not be found at {abs_path}.")
    except UnicodeDecodeError:
        raise Exception(
            f"There was an error decoding Config file from {config_path}. "
            f"Make sure your file is save using UTF-8"
        )


def _load_config(fp: TextIO) -> Dict[str, Any]:
    """
    Load the yaml config from the file-like object.
    """
    try:
        return yaml.safe_load(fp)
    except yaml.parser.ParserError as e:
        raise Exception(
            "Error parsing yaml file. Please check for formatting errors. "
            "A tool such as http://www.yamllint.com/ can be helpful with this."
        ) from e


def if_training_done(args, agent_name):
    folder = os.path.exists(args["file_path"] + agent_name + "/")
    if not folder:
        return True
    
    if os.path.exists(args["file_path"] + agent_name + '/Done'):
        return True

    return False
        
        
def Config(env_num=1, port=10000, file_path='./checkpoints/', agent_file_path='./checkpoints/', agent_name="MultiParallelPpoAITest"):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config_path", type=str, default="config.yaml", help="训练超参数的文件路径"
    )
    parser.add_argument(
        "--test_selfplay", type=str, default="false", help="在agent_file_path中进行测试"
    )
    parser.add_argument('--env', type=str, help="环境名称", default='FightingiceEnv-v0')
    parser.add_argument('--port', type=int, help="环境中的端口，用于区分Actor与环境通信使用。", default=port)

    parser.add_argument('--env_num', type=int, default=env_num) # env_num
    
    parser.add_argument('--gamma', type=float, default=0.9)
    parser.add_argument('--clip_ratio', type=float, default=0.2)
    parser.add_argument('--pi_lr', type=float, default=3e-4)
    parser.add_argument('--vf_lr', type=float, default=1e-3)
    parser.add_argument('--train_pi_iters', type=int, default=80)
    parser.add_argument('--train_v_iters', type=int, default=80)
    parser.add_argument('--lam', type=float, default=0.97)
    parser.add_argument('--target_kl', type=float, default=0.01)
    parser.add_argument('--save_freq', type=int, default=1)
    parser.add_argument('--seed', '-s', type=int, default=10000)
    parser.add_argument('--ac_networks_layer', type=int, default=2)

    parser.add_argument('--max_epochs', type=int, default=400)
    parser.add_argument('--steps_per_epoch', type=int, default=10000)
    parser.add_argument('--max_ep_len', type=int, default=1000)
    
    parser.add_argument('--elo_score', type=float, default=0)
    parser.add_argument('--character', type=str, default='ZEN') # ["ZEN", "GARNET", "LUD"]
    parser.add_argument('--test_round', type=int, default=10)

    parser.add_argument('--agents_name', type=str, help="训练Agent的原始名称", default=agent_name)

    parser.add_argument('--test_agent_name', type=str, help="测试的Agent名称（需要放到file_path下）", default=None)

    parser.add_argument('--file_path', type=str, help="训练完毕的Agent存储路径", default=file_path)
    
    parser.add_argument('--agent_file_path', type=str, help="训练过程中Agent的存储路径", default=agent_file_path)
    
    parser.add_argument('--fighting_data_file_path', type=str, help="双人对战的数据文件路径", default='/game_in_fighting_data.csv')
    parser.add_argument('--train_variable_file_path', type=str, help="训练时的数据文件路径", default='/game_in_train_variable.csv')
    parser.add_argument('--elo_opponents_file_path', type=str, help="Elo分数记录器的文件路径", default='/game_in_elo_opponents.csv')
    parser.add_argument('--elo_opponents_and_selfplay_file_path', help="在Selfplay过程中Elo分数记录器的文件路径", type=str, default='/game_in_elo_opponents_and_selfplay.csv')
    parser.add_argument('--winrate_opponents_file_path', type=str, help="winrate分数记录器的文件路径", default='/game_in_winrate_opponents.csv')
    parser.add_argument('--winrate_opponents_and_selfplay_file_path', help="在Selfplay过程中winrate分数记录器的文件路径", type=str, default='/game_in_winrate_opponents_and_selfplay.csv')
    parser.add_argument('--test_fighting_data_file_path', type=str, help="测试过程中的数据文件路径", default="/game_in_testing_fighting_data.csv")

    args = vars(parser.parse_args())

    if args["config_path"] != None:
        args = load_config(args["config_path"], args)
    if args["test_selfplay"] == "true":
        args["file_path"] = args["agent_file_path"]
    return args

def create_agent(args, agent_name):
    folder = os.path.exists(args["file_path"] + agent_name + "/")
    if not folder:
        os.makedirs(args["file_path"] + agent_name + "/")

def FrameConfig(args=None, env_num=1, agent_name='MultiParallelPpoAITest', agent_create_flag=None, port=10000, file_path='./checkpoints/', agent_file_path='./checkpoints/'):
    if args == None:
        args = Config(env_num=env_num, port=port, file_path=file_path, 
                            agent_file_path=agent_file_path, agent_name=agent_name)
    
    folder = os.path.exists(args["file_path"])
    if not folder:
        os.makedirs(args["file_path"])

    folder = os.path.exists(args["agent_file_path"])
    if not folder:
        os.makedirs(args["agent_file_path"])
        
    file_dir_list = os.listdir(args["file_path"])
    # print(len(file_dir_list))
    file_dir_list = [i for i in file_dir_list if re.match(args["agents_name"], i) != None]
    # print(len(file_dir_list))
    ai_num = len(file_dir_list)
    
    if agent_create_flag == None:
        agent_create_flag = if_training_done(args, args["agents_name"] + str(ai_num)) # 单机单Agent不走这破路
    if agent_create_flag or os.path.exists(args["file_path"] + args["agents_name"] + str(ai_num)) == False:
        agent_name = args["agents_name"] + str(ai_num + 1)
        # os.makedirs(args["file_path"] + agent_name + "/")
        create_agent(args, agent_name)
    else:
        agent_name = args["agents_name"] + str(ai_num)

    args["create_bot"] = agent_create_flag
    args["local_steps_per_epoch"] = math.ceil(args["steps_per_epoch"] / args["env_num"])
    args["agent_name"] = agent_name
    return args

def TestConfig(env_num=50, all_agent_test_flag=False):
    args = Config(env_num)
    agent_name = args["test_agent_name"]
    if agent_name == None or all_agent_test_flag:
        agent_name = None
        for name in os.listdir(args["file_path"]):
            if os.path.exists(args["file_path"] + name + args["test_fighting_data_file_path"]):
                continue
            agent_name = name
            break
    assert agent_name != None

    args["local_steps_per_epoch"] = math.ceil(args["steps_per_epoch"] / args["env_num"])
    args["agent_name"] = agent_name
    return args

def TestSelfplayConfig(env_num=50):
    args = Config(env_num)
    args["local_steps_per_epoch"] = math.ceil(args["steps_per_epoch"] / args["env_num"])
    args["agent_name"] = None
    return args

if __name__ == '__main__':
    FrameConfig()