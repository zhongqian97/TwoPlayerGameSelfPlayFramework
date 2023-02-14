
from copy import deepcopy
import numpy as np
import os

from Entity.Utils.bark_log import bark_log

class EloOpponents():
    def __init__(self, args):
        self.opp_ai_map = {}
        self.init(args)

    def init(self, args):
        self.args = args
        self.name = args["agent_name"] # 当前智能体名称
        self.dir_path = args["file_path"]
        
        self.opp_elo_dict = {}
        self.opp_win_rate_dict = {}
        
        self.opp_ai_list = args["opp_ai_list"]
        
        self.opp_ai_list_for_test = args["opp_ai_list_for_test"]
        
        for opp in self.opp_ai_list:
            self.opp_elo_dict[opp] = 0
            self.opp_ai_map[opp] = opp
            self.opp_win_rate_dict[opp] = 0
            
        self.the_end = False
            
    def clean_buffer(self):
        self.opp_ai_map = {}
        self.opp_elo_dict = {}
        self.opp_ai_list = []
        self.opp_win_rate_dict = {}
        print("clean_buffer")

    def add_all_test_bots(self):
        for bot in self.opp_ai_list_for_test:
            self.add(bot, bot)

    def add(self, name: str, data):
        """ 添加对手池的智能体

        Args:
            name (str): AI名称
            data (data): AI数据，Java为字符串，自博弈为一个类。
        """
        self.opp_ai_map[name] = data
        if name not in self.opp_ai_list:
            self.opp_ai_list.append(name)
        if name not in self.opp_elo_dict:
            self.opp_elo_dict[name] = 0
        if name not in self.opp_win_rate_dict:
            self.opp_win_rate_dict[name] = 0
        pass
    
    def _get_win(win):
        return 0 if win else 1

    def log(name, env, step, ep_len, ep_ret):
        opp = env.p2_name if env.p1_name == name else env.p1_name
        res = EloOpponents._get_win(env.win)
        opp_list = [opp, res]

        d = {"epoch": step, "length": ep_len, "return": ep_ret}
        if env.info != None and isinstance(env.info, dict):
            for k in env.info.keys():
                d[k] = env.info[k]

        csv_dict = d
        return opp_list, csv_dict
    
    def select_opponent(self, seed=0):
        _p2 = self.select_opponent_get_number(seed)
        return {"name": _p2, "agent": self.opp_ai_map[_p2]}

    def select_opponent_get_number(self, seed=0):
        opps, priorities = self._get_opp_priorities()
        pos = np.random.choice(len(opps), p=priorities)
        _p2 = opps[pos]
        return _p2
    
    def _get_opp_priorities_function(self, elo, win_rate, min_elo_list):
        # C = 1000
        # A = 5
        # W = 1.5
        # return ((A * (W - win_rate)) ** 2.0) * (elo + abs(min_elo_list) + C)
        return 1
        
    def _get_opp_priorities(self):
        # return all opps and selected priority
        # zhongqian
        opps = []
        priorities = []
        elo_list = []
        for opp in self.opp_elo_dict.keys():
            elo_list.append(self.opp_elo_dict[opp])
        min_elo_list = min(elo_list)

        for opp, elo in self.opp_elo_dict.items():
            opps.append(opp)
            win_rate = self.opp_win_rate_dict[opp]
            priorities.append(self._get_opp_priorities_function(elo, win_rate, min_elo_list))
        priorities = np.array(priorities)
        priorities = priorities / np.sum(priorities)
        return opps, priorities

    def _update_opp_elo(self, opp, result):
        # update opp elo according to opp vs ai game results
        # result = 1 if opp wins, 0 otherwise
        # opp vs ai winrate
        winrate = 1.0 / (1 + 10.0**((0-self.opp_elo_dict[opp])/400) )
        self.opp_elo_dict[opp] += 16 * (result-winrate)
    
    def theEnd(self):
        if self.args['if_open_selfplay'] == "True":
            return self.the_end
        else:
            return False
    
    def _calculate_the_winning_rate(self, opp_win_list):
        opp_win_round_dict = {}
        opp_all_round_dict = {}
        for opp in self.opp_elo_dict:
            opp_win_round_dict[opp] = 0
            opp_all_round_dict[opp] = 0

        for opp_win_data in opp_win_list:
            if opp_win_data[1] == 0: # win
                opp_win_round_dict[opp_win_data[0]] += 1
                
            opp_all_round_dict[opp_win_data[0]] += 1

        opp_win_rate_dict = {}
        for opp in self.opp_elo_dict:
            if opp_all_round_dict[opp] != 0:
                opp_win_rate_dict[opp] = opp_win_round_dict[opp] / opp_all_round_dict[opp]
            else:
                opp_win_rate_dict[opp] = 0

        # update the self.opp_win_rate_dict
        for opp in self.opp_elo_dict:
            if opp_all_round_dict[opp] != 0:
                self.opp_win_rate_dict[opp] = opp_win_rate_dict[opp]
        
        self.the_end = True
        for opp in self.opp_elo_dict:
            if self.opp_win_rate_dict[opp] < self.args["elo_winning_rate"]:
                self.the_end = False
                break

        if sum(self.opp_win_rate_dict.values()) / len(self.opp_win_rate_dict) < self.args["avg_elo_winning_rate"]:
            self.the_end = False
        pass

    def getOppDict(self):
        return self.opp_elo_dict

    def getWinrateDict(self):
        return self.opp_win_rate_dict

    def updateOppElo(self, opp_win_list):
        for opp_win in opp_win_list:
            self._update_opp_elo(opp_win[0], opp_win[1])
            
            # 更新胜率
        self._calculate_the_winning_rate(opp_win_list)

    def load(self, name):
        try:
            self.checkpoints_path_elo = self.args["file_path"] + name + "/opp_elo_list.npy"
            self.checkpoints_path_win = self.args["file_path"] + name + "/opp_winrate_list.npy"
            self.opp_elo_dict = np.load(self.checkpoints_path_elo, allow_pickle=True).item()
            self.opp_win_rate_dict = np.load(self.checkpoints_path_win, allow_pickle=True).item()
            print("load elo model success.")
        except Exception as e:
            print("load elo model failed", e)
        
    def save(self):
        np.save(self.checkpoints_path_elo, self.opp_elo_dict)
        np.save(self.checkpoints_path_win, self.opp_win_rate_dict)
        

