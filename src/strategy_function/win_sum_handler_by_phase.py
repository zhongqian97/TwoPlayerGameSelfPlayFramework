from operator import xor
from graph_function.Bar_Axis_Align_with_Tick import Axis_Align_with_Tick
from graph_function.Dataset_Simple import Dataset_Simple
from graph_function.bar_line_chart import bar_line_chart
from strategy_function.strategy_handler import StrategyHandler
import os
import csv
import numpy as np
import re
import yaml
import os, math
import re
import numpy as np
import argparse
from typing import Set, Dict, Any, TextIO
import os
from pip import main

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

class WinSumHandlerByPhase(StrategyHandler):
    def handleRequest(self, store_dict, request_name="WinSum"):
        request_list = [
            # "NoSFEloTest", 
            # "PpoAINoSFEloTest", 
            # "PpoAINoSFEloTestRandomChoose",
            # "PpoAINoSFEloTestSoftmax"
            "分阶段的胜场数对比"
        ]
        
        path_name_list = [
            # "temp/NoSFEloTest(20220423_Original_Version)",
            # "temp/PpoAINoSFEloTest(20220503)",
            # "temp/PpoAINoSFEloTestRandomChoose(20220501)",
            # "temp/PpoAINoSFEloTestSoftmax(20220506)"
            "temp/Phase"
            ]
        data_list = []
        name_list = ["", "与训练的对手", "与只测试的对手", "与全部的对手"]
        phase_list = ["无自博弈", "第一阶段", "第二阶段"]
        for name in name_list:
            data_list.append([name])
        for name in phase_list:
            data_list[0].append(name)
        bots_list = []
        args = load_config("./config.yaml", {})
        trained_bots = args["opp_ai_list"]
        test_bots = args["opp_ai_list_for_test"]
        bots = trained_bots + test_bots

        bots_list.append(trained_bots)
        bots_list.append(test_bots)
        bots_list.append(bots)
        
        for i in range(len(path_name_list)):
            request_name = request_list[i]
            path = "./" + path_name_list[i] + "/"
            dir_dict = self.getTestDataDict(path)
            for dir_name in dir_dict:
                agent_data_list = dir_dict[dir_name]
                for _ in range(1):
                    index = agent_data_list[0].index("isWin")
                    p1_index = agent_data_list[0].index("p1")
                    p2_index = agent_data_list[0].index("p2")
                    
                    for k in range(len(bots_list)):
                        win_sum = 0
                        bots = bots_list[k]
                        for win_sum_num in agent_data_list:
                            if win_sum_num[p1_index] in bots or win_sum_num[p2_index] in bots :
                                win_sum += 1 if win_sum_num[index] == "True" else 0
                
                        data_list[k + 1].append(win_sum)
            
            print(data_list)

            store_dict[request_name] = Dataset_Simple(title=request_name, 
                                                            data=data_list)

        return request_list