from graph_function.Bar_Axis_Align_with_Tick import Axis_Align_with_Tick
from graph_function.bar_line_chart import bar_line_chart
from strategy_function.strategy_handler import StrategyHandler
from strategy_function.strategy_handler import agent_name_sorted
import os
import csv
import numpy as np

class WinSumHandlerBySelfplayAgentIterEloValue(StrategyHandler):
    def add_elo_value(self, opp_elo, result):
        # update opp elo according to opp vs ai game results
        # result = 1 if opp wins, 0 otherwise
        # opp vs ai winrate
        winrate = 1.0 / (1 + 10.0**((0-opp_elo)/400) )
        # self.opp_elo_dict[opp] += 16 * (result-winrate)
        return 16 * (result-winrate)

    def winNum2Elo(self, win_num):
        ret = 0
        for i in range(10):
            if i < 10 - win_num:
                win_ret = 1
            else:
                win_ret = 0
            ret += self.add_elo_value(ret, win_ret)
        # 归一化
        ret = max(min(40, ret), -40)
        return ret

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
            bot_name_list = sorted(bot_name_list, key=agent_name_sorted)
            # bot_name_list.extend(["Thunder2021", "ERHEA_PI_DJL", "BlackMamba"])
            # bot_name_list = sorted(bot_name_list)

            for bot_name in bot_name_list:
                agent_data_list = dir_dict[dir_name]
                # split Opponent 
                request_agent_data_list = self.find(bot_name, agent_data_list)

                win_sum = 0
                index = agent_data_list[0].index("isWin")
                
                for win_sum_num in request_agent_data_list:
                    win_sum += 1 if win_sum_num[index] == "True" else 0
            
                xAxis_list.append(bot_name)
                # data_list.append(self.winNum2Elo(win_sum))
                data_list.append(win_sum / 10)
                # data_list.append(self.winNum2Elo(win_sum))

            xAxis_list.append(dir_name)
            data_list.append(0)
            xAxis_dict[dir_name] = xAxis_list
            # data_dict[dir_name] = list((np.array(data_list) - min(data_list)) / 80)
            data_dict[dir_name] = data_list
        store_data_dict = {}
        store_data_list = []
        for request_name in request_list:
            store_data = {}
            # print("title=")
            # print(request_name)
            # print("xAxis=")
            # print(xAxis_dict[request_name])
            # print("data=")
            # print(data_dict[request_name])
            # print(len(data_dict[request_name]))
            # print(len(xAxis_dict[request_name]))
            assert len(data_dict[request_name]) == len(xAxis_dict[request_name])
            store_data["name"] = request_name
            store_data["opp"] = xAxis_dict[request_name]
            store_data["data"] = data_dict[request_name]
            store_data_dict[request_name] = store_data
            store_data_list.append(store_data)
            store_dict[request_name] = Axis_Align_with_Tick(title=request_name, 
                                                            xAxis=xAxis_dict[request_name], 
                                                            data=data_dict[request_name], 
                                                            bar_or_line_type=True,
                                                            yMin=min(data_dict[request_name]),
                                                            yMax=max(data_dict[request_name]))
        # np.save("store_data_dict.npy", store_data_dict)
        import json
        info_json = json.dumps(store_data_dict,sort_keys=False, indent=4, separators=(',', ': '))
        f = open('store_data_dict.json', 'w')
        f.write(info_json)
        f.close()

        info_json = json.dumps(store_data_list,sort_keys=False, indent=4, separators=(',', ': '))
        f = open('store_data_list.json', 'w')
        f.write(info_json)
        f.close()
        return reversed(request_list)