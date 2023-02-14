import os, math
import numpy as np
import argparse
from typing import Set, Dict, Any, TextIO
import os
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


if __name__ == '__main__':
    args = load_config("./config.yaml", {})
    character = "ZEN"
    test_round = args["test_round"]
    opp_ai_list = args["opp_ai_list"] 
    opp_ai_list.extend(args["opp_ai_list_for_test"])
    for i in range(len(opp_ai_list)):
        for k in range(len(opp_ai_list)):
            if i == k:
                continue
            p1 = opp_ai_list[i]
            p2 = opp_ai_list[k]
            exe_command = "java -Dai.djl.logging.level=debug -cp ./Entity/Env/FTG4.50/FightingICE.jar:./Entity/Env/FTG4.50/lib/lwjgl/*:./Entity/Env/FTG4.50/lib/natives/linux/*:./Entity/Env/FTG4.50/lib/*:./Entity/Env/FTG4.50/lib/erheajar/* Main --a1 {} --a2 {} --c1 {} --c2 {} -n {}".format(p1, p2, character, character, test_round)
            os.system(exe_command)
    pass