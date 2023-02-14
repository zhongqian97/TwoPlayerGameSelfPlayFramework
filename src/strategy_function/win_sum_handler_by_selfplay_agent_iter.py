from graph_function.Bar_Axis_Align_with_Tick import Axis_Align_with_Tick
from graph_function.bar_line_chart import bar_line_chart
from strategy_function.strategy_handler import StrategyHandler
import os
import csv
import numpy as np

class WinSumHandlerBySelfplayAgentIter(StrategyHandler):

    def handleRequest(self, store_dict, request_name="WinSum"):
        xAxis_dict = {}
        data_dict = {}

        ##########################
        path_name_list = ["temp/ParallelPpgAINoSFEloTest0_V64_WR60_WRA0"]
        ##########################

        request_list = []
        dir_dict = self.getTestDataDictList(path_name_list)
        path_name = path_name_list[0]
        for dir_name in dir_dict:
            request_list.append(dir_name)
            xAxis_list = []
            data_list = []

            path = "./" + path_name + "/" + dir_name + "/opp_elo_list.npy"
            bot_name_list = np.load(path, allow_pickle=True).item()
            bot_name_list = list(bot_name_list.keys())
            # bot_name_list.extend(["Thunder2021", "BlackMamba", "ERHEA_PI_DJL"])
            bot_name_list = sorted(bot_name_list)

            for bot_name in bot_name_list:
                agent_data_list = dir_dict[dir_name]
                # split Opponent 
                request_agent_data_list = self.find(bot_name, agent_data_list)

                win_sum = 0
                index = agent_data_list[0].index("isWin")
                
                for win_sum_num in request_agent_data_list:
                    win_sum += 1 if win_sum_num[index] == "True" else 0
            
                xAxis_list.append(bot_name)
                data_list.append(win_sum)

            xAxis_dict[dir_name] = xAxis_list
            data_dict[dir_name] = data_list

        for request_name in request_list:
            store_dict[request_name] = Axis_Align_with_Tick(title=request_name, 
                                                            xAxis=xAxis_dict[request_name], 
                                                            data=data_dict[request_name], 
                                                            bar_or_line_type=True,
                                                            yMin=min(data_dict[request_name]) - 5,
                                                            yMax=max(data_dict[request_name]))
        return reversed(request_list)