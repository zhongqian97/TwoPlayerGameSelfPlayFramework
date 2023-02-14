from graph_function.Stacked_Area_Chart import stacked_area_chart
from graph_function.Bar_Axis_Align_with_Tick import Axis_Align_with_Tick
from graph_function.bar_line_chart import bar_line_chart
from strategy_function.strategy_handler import StrategyHandler
import os
import csv
import numpy as np


class WinSumHandlerByEachStep(StrategyHandler):
    def handleRequest(self, store_dict, request_name="WinSum"):
        request_list = [
                        # "PpoAINoSFEloTestRandomChoose",
                        # "PpoAINoSFEloAndWinRateTest"
                        # "PpoAINoSFEloTestRandomChooseRewadDel2000",
                        # "PpoAINoSFEloTestRandomChooseRewadDel2000Change"
                        # "PpoAINoSFEloTestRewadTop2000"
                        "PpoAINoSFEloTest0_V64",
                        "PpgAINoSFEloTest0"
                        ]
        
        path_name_list = [
            # "temp/PpoAINoSFEloTestRandomChoose(20220510)",
            # "temp/PpoAINoSFEloTestRandomChoose2000",
            # # "temp/PpoAINoSFEloAndWinRateTest0"
            # "temp/PpoAINoSFEloAndWinRateTest2000"
            # "temp/PpoAINoSFEloTestRandomChooseRewadDel2000",
            # "temp/PpoAINoSFEloTestRandomChooseRewadDel2000Change"
            # "temp/PpoAINoSFEloTestRewadTop2000"
            "temp/PpoAINoSFEloTest0_V64",
            "temp/PpgAINoSFEloTest0"
            ]
        for i in range(len(path_name_list)):
            xAxis_list = [num for num in range(0, 110, 5)]
            # xAxis_list.append("test")
            data_list = []
            agent_name_list = []
            request_name = request_list[i]
            path = "./" + path_name_list[i] + "/"
            dir_dict = self.getTestDataDict(path)
            for dir_name in dir_dict:
                agent_data_list = dir_dict[dir_name]

                win_sum_list_by_each_step = []
                index = agent_data_list[0].index("isWin")
                for num in xAxis_list:
                    win_sum = 0
                    
                    for win_sum_num in agent_data_list:
                        if win_sum_num[0] == str(num):
                            win_sum += 1 if win_sum_num[index] == "True" else 0

                    win_sum_list_by_each_step.append(win_sum)
            
                data_list.append(win_sum_list_by_each_step)
                agent_name_list.append(dir_name)
            
            # print(xAxis_list)
            # print(path  + ": " + str(np.mean(data_list)))

            # store_dict[request_name] = Axis_Align_with_Tick(title=request_name, 
            #                                                 xAxis=xAxis_list, 
            #                                                 data=data_list, 
            #                                                 bar_or_line_type=True,
            #                                                 yMin=min(data_list) - 5,
            #                                                 yMax=max(data_list))

            # stacked_area_chart(title: str, xAxis: list, agent_name_list: list, data: list, yMin = 0, yMax = 400)

            store_dict[request_name] = stacked_area_chart(title=request_name, 
                                                        xAxis=xAxis_list,
                                                        agent_name_list=agent_name_list,
                                                        data=data_list)
        return request_list