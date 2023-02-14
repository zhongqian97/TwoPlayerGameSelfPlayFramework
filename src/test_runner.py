from copy import copy
from re import I
import time
from Entity.Agent.test_worker import TestWorker, TestWorkerParallel
from Entity.Agent.trainer import Trainer
from Entity.Elo.SelfplayEloOpponents import SelfplayEloOpponents
from Entity.Utils.bark_log import bark_log
from Entity.Utils.log import Logger


import gym
import myenv
import ray
import numpy as np
import os, math, copy

from Entity.Utils.config import TestConfig

def split_list(input_queue, env_num):
    input_queue_clip = []
    n = len(input_queue)
    if n % env_num == 0:
        input_queue_clip = [input_queue[i: i + (n // env_num)] for i in range(0, env_num * (n // env_num), (n // env_num))]
    else:
        x = n // env_num
        k = n - (x) * env_num # k个(n//env_num + 1)
        input_queue_clip = [input_queue[i: i + (x + 1)] for i in range(0, k * (x + 1), (x + 1))]
        
        input_queue_x = input_queue[k * (x + 1):]
        for i in range(0, (env_num - k) * x, x):
            l = input_queue_x[i: i + x]
            input_queue_clip.append(l)

    return input_queue_clip

def Testing(args):
    elo_opponents = SelfplayEloOpponents(args)
    env = gym.make(args["env"])
    trainer = Trainer(env=env, args=args)
    
    fighting_data_logger = Logger(
        args["file_path"] + args["agent_name"] + args["test_fighting_data_file_path"], args["fighting_data_csv"])
    trainer.load(args["agent_name"])

    # TODO 整合 + 拆分
    input_queue = []
    opp_list = []
    opp_list.extend(elo_opponents.opp_ai_list)
    opp_list.extend(elo_opponents.opp_ai_list_for_test)
    
    for opp in opp_list:
        for p1_flag in [True, False]:
            input_info = {}
            input_info["p2_bot"] = {"name": opp, "agent": opp}
            input_info["p1_flag"] = p1_flag
            for _ in range(args["test_round"]):
                    input_queue.append(input_info)
        pass
    
    agents = [TestWorkerParallel.remote
            (args, i, [], [], elo_opponents, trainer.get_weights()) for i in range(args["env_num"])]
    
    while True:
        n = len(input_queue)
        if n == 0:
            break
        if len(input_queue) > args["env_num"]:
            input_queue_clip = split_list(input_queue, args["env_num"])
            buffers_ids = [
                    agents[i].testing.remote(input_queue_clip[i]) for i in range(args["env_num"])
                ]
            n = args["env_num"]
        else:
            buffers_ids = [
                    agents[i].testing.remote([input_queue[i]]) for i in range(n)
                ]
        
        fighting_data_map_list = []

        times = 100 * args["test_round"]
        for _ in range(n):
            # try:
            [buffers_id], buffers_ids = ray.wait(buffers_ids) # , timeout=times)
            # except Exception:
            #     # for id in buffers_ids:
            #     #     ray.cancel(id)
            #     break
            fighting_data_map_info = ray.get(buffers_id)
            for fighting_data_map in fighting_data_map_info:
                for i in range(len(input_queue)):
                    if input_queue[i]["p2_bot"] == fighting_data_map["p2_bot"] and input_queue[i]["p1_flag"] == fighting_data_map["p1_flag"]:
                        del input_queue[i]
                        break
            for fighting_data_map in fighting_data_map_info:
                fighting_data_map_list.extend(copy.deepcopy(fighting_data_map["fighting_data_map_list"]))
        pass
    fighting_data_logger.log()
    fighting_data_logger.list_log(lists=fighting_data_map_list)
    
    env.close()
    trainer.close()
    buffers_ids = [agent.close.remote() for agent in agents]
    for _ in range(args["env_num"]):
        [buffers_id], buffers_ids = ray.wait(buffers_ids)
    pass

    return True
    
if __name__ == '__main__':
    ray.init(address='auto', _redis_password='5241590000000000')
    args = TestConfig()
    import json
    print(json.dumps(args))
    Testing(args)