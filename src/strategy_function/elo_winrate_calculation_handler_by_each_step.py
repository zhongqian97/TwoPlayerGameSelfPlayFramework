# from graph_function.Stacked_Area_Chart import stacked_area_chart
# from graph_function.Bar_Axis_Align_with_Tick import Axis_Align_with_Tick
# from graph_function.bar_line_chart import bar_line_chart
# from strategy_function.strategy_handler import StrategyHandler
# import os
# import csv
# import numpy as np
# class ArgsX():
#     agent_name = ""
#     file_path = ""
#     elo_winning_rate = 0

# class EloWinrateCalculationHandlerByEachStep(StrategyHandler):
#     def handleRequest(self, store_dict, request_name="WinSum"):
#         # request_list = ["PpoAINoSFEloTestRandomChoose"]
#         request_list = [num for num in range(1, 100, 5)]
#         true_request_list = []
#         xAxis_list = ["TeraThunder", 
#                             "CYR_AI", 
#                             "BCP", 
#                             "JayBot_GM", 
#                             "EmcmAi",
#                             "DiceAI", 
#                             "KotlinTestAgent",
#                             "Dora", 
#                             "LGIST_Bot", 
#                             "Toothless",
#                             "FalzAI", 
#                             "ReiwaThunder", 
#                             "TOVOR",
#                             "HaibuAI", 
#                             "MctsAi", 
#                             "UtalFighter"
#                             # ,
#                             # "Thunder2021", 
#                             # "BlackMamba", 
#                             # "ERHEA_PI_DJL"
#                             ]
        
#         path_name_list = [
#             # "temp/PpoAINoSFEloTestRandomChoose(20220510)",
#             "temp/PpoAINoSFEloAndWinRateTest0"
#             ]

#         elo_opponents = EloOpponents(ArgsX())
#         for i in range(len(path_name_list)):
#             path = "./" + path_name_list[i] + "/"
#             train_dir_dict = self.getTrainDataDict(path)
#             elo_agent_dict = self.getDataDict(path, "game_in_elo_opponents.csv")

#             for dir_name in train_dir_dict:
#                 agent_data_list = train_dir_dict[dir_name]

#                 is_win_index = agent_data_list[0].index("isWin")
#                 p1_index = agent_data_list[0].index("p1")
#                 p2_index = agent_data_list[0].index("p2")

#                 for k in range(len(request_list)):
#                     data_list = []
#                     request_name = round_num = request_list[k]
#                     request_name = str(request_name)

#                     opp_win_list = []
#                     for win_sum_num in agent_data_list:
#                         if win_sum_num[0] == str(round_num):
#                             opp_win = []
#                             opp_win.append(win_sum_num[p2_index] if win_sum_num[p1_index] == dir_name else win_sum_num[p1_index])
#                             opp_win.append(elo_opponents._get_win(win_sum_num[is_win_index] == "True"))
#                             opp_win_list.append(opp_win)
#                     elo_opponents.updateOppElo(opp_win_list)

#                     opps, priorities = elo_opponents._get_opp_priorities()

#                     store_dict["priorities_" + request_name] = Axis_Align_with_Tick(title="priorities_" + request_name, 
#                                                                     xAxis=opps, 
#                                                                     data=priorities, 
#                                                                     bar_or_line_type=True,
#                                                                     yMin=0,
#                                                                     yMax=1)
#                     opp_win_rate_list = []
#                     for opp in opps:
#                         opp_win_rate_list.append(elo_opponents.opp_win_rate_dict[opp])
                    
#                     store_dict["winrate_" + request_name] = Axis_Align_with_Tick(title="winrate_" + request_name, 
#                                                                     xAxis=opps, 
#                                                                     data=opp_win_rate_list, 
#                                                                     bar_or_line_type=True,
#                                                                     yMin=0,
#                                                                     yMax=1)
#                     true_request_list.append("priorities_" + request_name)
#                     true_request_list.append("winrate_" + request_name)
                    
#         return true_request_list