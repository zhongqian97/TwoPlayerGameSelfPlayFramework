from graph_function.Bar_Axis_Align_with_Tick import Axis_Align_with_Tick
from graph_function.bar_line_chart import bar_line_chart
from strategy_function.strategy_handler import StrategyHandler
import os
import csv

class WinSumHandlerBySingleAgent(StrategyHandler):

    def handleRequest(self, store_dict, request_name="WinSum"):
        request_list = ["TeraThunder", 
                            # "CYR_AI", 
                            # "BCP", 
                            "JayBot_GM", 
                            "EmcmAi",
                            # "DiceAI", 
                            # "KotlinTestAgent",
                            # "Dora", 
                            "LGIST_Bot", 
                            # "Toothless",
                            "FalzAI", 
                            "ReiwaThunder", 
                            # "TOVOR",
                            # "HaibuAI", 
                            # "MctsAi", 
                            # "UtalFighter",
                            "Thunder2021", 
                            "BlackMamba", 
                            "ERHEA_PI_DJL"]

        # request_list = ["TeraThunder", 
        #                     "CYR_AI", 
        #                     "BCP", 
        #                     "JayBot_GM", 
        #                     "EmcmAi",
        #                     "DiceAI", 
        #                     "KotlinTestAgent",
        #                     "Dora", 
        #                     "LGIST_Bot", 
        #                     "Toothless",
        #                     "FalzAI", 
        #                     "ReiwaThunder", 
        #                     "TOVOR",
        #                     "HaibuAI", 
        #                     "MctsAi", 
        #                     "UtalFighter",
        #                     "Thunder2021", 
        #                     "BlackMamba", 
        #                     "ERHEA_PI_DJL"]
        
        xAxis_dict = {}
        data_dict = {}
        path_name_list = [
            # "temp/NoSFEloTest(20220423_Original_Version)",
            # "temp/PpoAINoSFEloTest(20220503)",
            # "temp/PpoAINoSFEloTestRandomChoose(20220501)",
            # "temp/PpoAINoSFEloTestSoftmax(20220506)"
            # "checkpoints"
            "temp/ParallelPpgAINoSFEloTest0_V64_WR60_WRA0"
            # "temp/ParallelPpgAINoSFEloTest0_V64_WR85"
            ]
        dir_dict = self.getTestDataDictList(path_name_list)
        for request_name in request_list:
            xAxis_list = []
            data_list = []
            for dir_name in dir_dict:
                agent_data_list = dir_dict[dir_name]
                # split Opponent 
                request_agent_data_list = self.find(request_name, agent_data_list)

                win_sum = 0
                index = agent_data_list[0].index("isWin")
                
                for win_sum_num in request_agent_data_list:
                    win_sum += 1 if win_sum_num[index] == "True" else 0
            
                xAxis_list.append(dir_name)
                data_list.append(win_sum)

            xAxis_dict[request_name] = xAxis_list
            data_dict[request_name] = data_list

        for request_name in request_list:
            store_dict[request_name] = Axis_Align_with_Tick(title=request_name, 
                                                            xAxis=xAxis_dict[request_name], 
                                                            data=data_dict[request_name], 
                                                            bar_or_line_type=True,
                                                            yMin=min(data_dict[request_name]) - 5,
                                                            yMax=max(data_dict[request_name]))
        return request_list