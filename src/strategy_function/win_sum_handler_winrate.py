from operator import xor
from graph_function.Bar_Axis_Align_with_Tick import Axis_Align_with_Tick
from graph_function.bar_line_chart import bar_line_chart
from strategy_function.strategy_handler import StrategyHandler
import os
import csv
import numpy as np
import re


class WinSumHandlerWinrate(StrategyHandler):
    def handleRequest(self, store_dict, request_name="WinSum"):
        request_list = [
            # "NoSFEloTest", 
            # "PpoAINoSFEloTest", 
            # "PpoAINoSFEloTestRandomChoose",
            # "PpoAINoSFEloTestSoftmax"
            "自博弈对手池总体（固定Bot以及自博弈Agent）测试胜率"
        ]
        
        path_name_list = [
            # "temp/NoSFEloTest(20220423_Original_Version)",
            # "temp/PpoAINoSFEloTest(20220503)",
            # "temp/PpoAINoSFEloTestRandomChoose(20220501)",
            # "temp/PpoAINoSFEloTestSoftmax(20220506)"
            # "checkpoints"
            "temp/ParallelPpgAINoSFEloTest0_V64_WR60_WRA0"
            ]
        for i in range(len(path_name_list)):
            xAxis_list = []
            data_list = []
            request_name = request_list[i]
            path = "./" + path_name_list[i] + "/"
            dir_dict = self.getTestDataDict(path)
            for dir_name in dir_dict:
                agent_data_list = dir_dict[dir_name]

                win_sum = 0
                win_all = 0
                index = agent_data_list[0].index("isWin")
                p1_index = agent_data_list[0].index("p1")
                p2_index = agent_data_list[0].index("p2")
                
                for win_sum_num in agent_data_list:
                    if (re.match('ParallelPpgAINoSFEloTest', win_sum_num[p1_index]) == None) ^ (re.match('ParallelPpgAINoSFEloTest', win_sum_num[p2_index]) == None):
                        win_sum += 1 if win_sum_num[index] == "True" else 0
                        win_all += 1
            
                xAxis_list.append(dir_name)
                data_list.append(win_sum / win_all)
            
            # print(xAxis_list)
            print(path  + ": " + str(np.mean(data_list)))

            store_dict[request_name] = Axis_Align_with_Tick(title=request_name, 
                                                            xAxis=xAxis_list, 
                                                            data=data_list, 
                                                            bar_or_line_type=True,
                                                            yMin=0,
                                                            yMax=1)

        return request_list