from calendar import c
import copy
import time
from Entity.Agent.ppo_buffer import RayBuffer
from Entity.Agent.rollout_worker import ModelRollout, RolloutWorkerParallel
from Entity.Agent.trainer import Trainer
from Entity.Elo.SelfplayEloOpponents import SelfplayEloOpponents
from Entity.Utils.bark_log import bark_log
from Entity.Utils.log import Logger

from Entity.Elo.EloOpponents import EloOpponents

from Entity.Utils.config import FrameConfig

import gym
import myenv
import ray
import numpy as np
import os

# ray.init(address="10.1.20.132:6000", _redis_password='5241590000000000')

def Running(args):
    elo_opponents = SelfplayEloOpponents(args)
    env = gym.make(args["env"])
    trainer = Trainer(env=env, args=args)
    agents = [RolloutWorkerParallel.remote(
        args, _) for _ in range(args["env_num"])]

    fighting_data_logger = Logger(
        args["file_path"] + args["agent_name"] + args["fighting_data_file_path"], args["fighting_data_csv"])
    train_variable_logger = Logger(
        args["file_path"] + args["agent_name"] + args["train_variable_file_path"], trainer.get_train_maps_list())
    elo_opponents_logger = Logger(
        args["file_path"] + args["agent_name"] + args["elo_opponents_file_path"], elo_opponents.opp_ai_list)
    winrate_opponents_logger = Logger(
        args["file_path"] + args["agent_name"] + args["winrate_opponents_file_path"], elo_opponents.opp_ai_list)

    start_epoch = trainer.load(args["agent_name"])
    elo_opponents.load(args["agent_name"])
    theEndFlag = False
    
    if start_epoch == 1:
        fighting_data_logger.log()
        train_variable_logger.log()
        elo_opponents_logger.log()
        winrate_opponents_logger.log()
    else:
        start_epoch += 1
        
        if os.path.exists(args["file_path"] + args["agent_name"] + args["elo_opponents_and_selfplay_file_path"]):
            _, elo_opponents_logger, winrate_opponents_logger = Elo2Selfplay(args, elo_opponents)
            if elo_opponents.theEnd():
                return True
            theEndFlag = True
            pass

    for i in range(start_epoch, 1 + args["max_epochs"]):
        print("现在已经第%d代" % (i))

        modelRollout = ModelRollout(trainer.get_weights(), i, elo_opponents)
        model_id = ray.put(modelRollout)

        buffers_ids = [
            agent.rollout.remote(model_id) for agent in agents
        ]
        samples = RayBuffer()
        fighting_data_map_list = []
        opp_elo_list = []
        for batch in range(args["env_num"]):
            [buffers_id], buffers_ids = ray.wait(buffers_ids)
            sample, fighting_data_map, opp_elo = ray.get(buffers_id)

            opp_elo_list.extend(copy.deepcopy(opp_elo))
            fighting_data_map_list.extend(copy.deepcopy(fighting_data_map))
            samples.put(copy.deepcopy(sample))

        elo_opponents.updateOppElo(opp_elo_list)
        train_variable_logger.log(maps=trainer.train(samples.get(), i))
        fighting_data_logger.list_log(lists=fighting_data_map_list)
        elo_opponents_logger.log(maps=elo_opponents.getOppDict())
        winrate_opponents_logger.log(maps=elo_opponents.getWinrateDict())

        trainer.save(i)
        elo_opponents.save()

        if theEndFlag and elo_opponents.theEnd():
            print(args["agent_name"] + "认为自博弈训练完毕。")
            print(args["agent_name"] + "认为自博弈训练完毕。")
            print(args["agent_name"] + "认为自博弈训练完毕。")
            print(args["agent_name"] + "认为自博弈训练完毕。")
            print(args["agent_name"] + "认为自博弈训练完毕。")
            break

        elif elo_opponents.theEnd():
            print(args["agent_name"] + "认为对手池内对手已经太弱鸡了！上自博弈。")
            print(args["agent_name"] + "认为对手池内对手已经太弱鸡了！上自博弈。")
            print(args["agent_name"] + "认为对手池内对手已经太弱鸡了！上自博弈。")
            print(args["agent_name"] + "认为对手池内对手已经太弱鸡了！上自博弈。")
            print(args["agent_name"] + "认为对手池内对手已经太弱鸡了！上自博弈。")
            theEndFlag = True
            done, elo_opponents_logger, winrate_opponents_logger = Elo2Selfplay(args, elo_opponents)
            if done:
                break
            elo_opponents_logger.log()
            winrate_opponents_logger.log()
            pass
    
    env.close()
    trainer.close()
    buffers_ids = [agent.close.remote() for agent in agents]
    for batch in range(args["env_num"]):
        [buffers_id], buffers_ids = ray.wait(buffers_ids)
    elo_opponents.move(args)
    return True

def Elo2Selfplay(args, elo_opponents):
    """从Elo转成Selfplay过程

    Args:
        args (_type_): _description_
        elo_opponents (_type_): _description_

    Returns:
        bool: 是否已经添加完毕智能体
    """
    env = gym.make(args["env"])
    if elo_opponents.addSelfplayEloOpponent(args, env):
        env.close()
        return True, None, None
    env.close()
    elo_opponents_logger = Logger(
        args["file_path"] + args["agent_name"] + args["elo_opponents_and_selfplay_file_path"], elo_opponents.opp_ai_list)
    
    winrate_opponents_logger = Logger(
        args["file_path"] + args["agent_name"] + args["winrate_opponents_and_selfplay_file_path"], elo_opponents.opp_ai_list)
    print(elo_opponents.opp_ai_list)
    
    return False, elo_opponents_logger, winrate_opponents_logger

if __name__ == '__main__':
    ray.init()
    args = FrameConfig()
    import json
    print(json.dumps(args))
    Running(args)