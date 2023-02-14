import os
import csv
from Entity.Utils.config import TestConfig 
from projected_replicator_dynamics import projected_replicator_dynamics
import numpy as np

agent_name_list = []

def getTestDataList(path):
    """game_in_testing_fighting_data.csv 加载器
    """
    test_data_list = []
    csv_file_path = path + '/game_in_testing_fighting_data.csv'
    if os.path.exists(csv_file_path) == False:
        return []
    with open(csv_file_path) as f:
        f_csv = csv.reader(f)
        f_csv = list(f_csv)
        test_data_list = f_csv
            
    return test_data_list

def CalculatePayoffMatrix(file_name):
    agent_data_list = getTestDataList(file_name)
    payoff_list = []
    win_sum = 0
    p1_index = agent_data_list[0].index("p1")
    p2_index = agent_data_list[0].index("p2")
    p1_hp_index = agent_data_list[0].index("p1_hp")
    p2_hp_index = agent_data_list[0].index("p2_hp")
    
    for agent_name in agent_name_list:
        payoff_agent_name_list = []
        for opp_name in agent_name_list:
            win_sum = 0
            len_sum = 0
            if agent_name == opp_name:
                payoff_agent_name_list.append(0)
                continue
            for win_sum_num in agent_data_list:
                if (win_sum_num[p1_index] == agent_name and win_sum_num[p2_index] == opp_name) or (win_sum_num[p2_index] == agent_name and win_sum_num[p1_index] == opp_name):
                    len_sum += 1
                    if win_sum_num[p1_index] == agent_name and win_sum_num[p1_hp_index] > win_sum_num[p2_hp_index]:
                        win_sum += 1
                    if win_sum_num[p2_index] == agent_name and win_sum_num[p2_hp_index] > win_sum_num[p1_hp_index]:
                        win_sum += 1
            if len_sum != 0:
                payoff_agent_name_list.append(win_sum / len_sum)
            else:
                payoff_agent_name_list.append(-1)
            
        payoff_list.append(payoff_agent_name_list)
    return payoff_list


if __name__ == '__main__':
    args = TestConfig()
    opp_ai_list = args["opp_ai_list"]
    opp_ai_list_for_test = args["opp_ai_list_for_test"]
    
    agent_name_list = ["ParallelPpgAINoSFEloTest0" + str(i + 1) for i in range(len(os.listdir("./temp/ParallelPpgAINoSFEloTest0_V64_WR85")))]
    payoff_list = CalculatePayoffMatrix("selfplay/2022-06-15_21-03-39")
    print("payoff_list: ")
    for i in range(len(agent_name_list)):
        print(payoff_list[i])

    test_a =  np.array(payoff_list)
    test_b =  np.array(payoff_list).T

    # test_a = np.array([[0, 1, -1], 
    #                 [-1, 0, 1], 
    #                 [1, -1, 0]])
    # test_b = np.array([[0, -1, 1], 
    #                 [1, 0, -1], 
    #                 [-1, 1, 0]])

    strategies = projected_replicator_dynamics(
        [test_a, test_b],
        prd_initial_strategies=None,
        prd_iterations=50000,
        prd_dt=1e-3,
        prd_gamma=1e-8,
        average_over_last_n_strategies=10)
    
    print("strategies: ")
    print(strategies)
    pass