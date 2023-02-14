from ast import Try
from random import random
from ray.util.queue import Queue
import ray

from Entity.Task.task import ATask
import copy
import time
from Entity.Agent.ppo_buffer import RayBuffer
from Entity.Agent.rollout_worker import ModelRollout, RolloutWorkerParallel
from Entity.Agent.trainer import Trainer
from Entity.Elo.SelfplayEloOpponents import SelfplayEloOpponents
from Entity.Utils.bark_log import bark_log
from Entity.Utils.log import Logger
from Entity.Utils.config import FrameConfig
from Entity.Agent.rl_agent_factory import CreateAgent

import gym
import myenv
import numpy as np
import os
import gc

@ray.remote(num_cpus=1)
class TestTask(ATask):
    def __init__(self, args) -> None:
        super().__init__()
        self.args = args
        self.queue = Queue()
        self.status = "pre_handle"
        self.queue_clear = None
        self.elo_opponents = None

    def set_self_and_next(self, self_task, next_task):
        self.self_task = self_task
        self.next_task = next_task

    def set_args(self, args):
        self.args = args

    def set_elo_opponents(self, elo_opponents):
        self.elo_opponents = copy.deepcopy(elo_opponents) 

    def _init(self):
        self.opp_elo_list = []
        self.fighting_data_map_list = []
        self.queue_clear = None
        self.agents = {"name": self.agent_name, "agent": self.trainer}
        self.trainer_id = ray.put(self.agents)
        print("现在已经第%d代" % (self.iterations))

    def processing(self):
        """并行使用调用器
        """
        if self.status == "pre_handle":
            self.preHandle()
            self.status = "handling_and_create"
            self.iterations = self.start_epoch
            self._init()

        elif self.status == "handling_and_create":
            # 处理buffer_size
            if self.queue.empty() == False:
                post_handle_flag = self.handling()
                if post_handle_flag:
                    self.status = "post_handle"
            pass

        elif self.status == "post_handle":
            if self.postHandle():
                self.status = "end"
            else:
                self.status = "handling_and_create"
                self.iterations += 1
                if self.args["max_epochs"] < self.iterations:
                    self.status = "end"
                self._init()
        elif self.status == "end":
            self.end()
            pass
        pass
        
    def preHandle(self):
        """从零开始做训练，这里主要用于训练前的文件夹创建的等等。
        """
        import myenv
        self.agent_name = self.args["agent_name"]
        env = gym.make(self.args["env"])
        self.trainer = CreateAgent(args=self.args, env=env)
        if self.elo_opponents == None:
            self.elo_opponents = SelfplayEloOpponents(self.args)
        self.elo_opponents.add_all_test_bots()
        self.elo_opponents.addSelfplayEloOpponent(self.args, env)
        self.test_fighting_data_logger = Logger(
            self.args["file_path"] + self.agent_name + self.args["test_fighting_data_file_path"], self.args["fighting_data_csv"])

        # self.elo_opponents.load(self.agent_name)
        self.start_epoch = self.trainer.load(self.agent_name)

        env.close() 
        # Elo对手放入对手池
        # self.opp_ai_map_ray = {}
        # for name in self.elo_opponents.opp_ai_map.keys():
        #     d = {"name": name, "agent": self.elo_opponents.opp_ai_map[name]}
        #     self.opp_ai_map_ray[name] = ray.put(d)
        # pass

        opp_list = copy.deepcopy(self.elo_opponents.opp_ai_list)
        self.input_queue = []
        for opp in opp_list:
            for p1_flag in [True, False]:
                input_info = {}
                input_info["p2_bot"] = {"name": opp, "agent": self.elo_opponents.opp_ai_map[opp]}
                input_info["p1_flag"] = p1_flag
                for _ in range(self.args["test_round"]):
                    self.input_queue.append(input_info)
            pass

    def _get_can_use_buffer(self):
        input_dict = self.input_queue[np.random.choice(len(self.input_queue))]
        return input_dict["p2_bot"], input_dict["p1_flag"]

    def create(self):
        """创建内容使用，Opponent choose在这里使用。
        """
        if len(self.input_queue) == 0:
            return None
        p2_bot, p1_flag = self._get_can_use_buffer()
        models = {}
        models["step"] = self.iterations
        models["p1_flag"] = p1_flag
        models["p2_bot"] = p2_bot
        models["p1_runner"] = self.agents
        models["output_queue"] = self.queue
        models["task"] = self.self_task
        models_id = ray.put(models)
        return models_id

    def processing_and_get_status(self):
        self.processing()
        return self.get_status()

    def get_status(self):
        return self.status

    def compare_status(self, step):
        return True

    def handling(self):
        """放入buffer，并处理训练前的细节。
        首先将信息放入buffer中，
        """
        self.status = "handling_no_create"
        finish_buffer_flag = False
        while self.queue.empty() == False:
            trajectory = self.queue.get()
            store_list = trajectory["store_list"]
            fighting_data_map = trajectory["csv_list"]
            opp_list = trajectory["opp_list"]

            if fighting_data_map["epoch"] != self.iterations:
                continue
            if self.agent_name == fighting_data_map["p1"]:
                p2_bot = fighting_data_map["p2"]
                p1_flag = True
            else:
                p2_bot = fighting_data_map["p1"]
                p1_flag = False

            for i in range(len(self.input_queue)):
                if self.input_queue[i]["p2_bot"]["name"] == p2_bot and self.input_queue[i]["p1_flag"] == p1_flag:
                    del self.input_queue[i]
                    self.fighting_data_map_list.append(copy.deepcopy(fighting_data_map))
                    break
                
            # trajectory

            if len(self.input_queue) == 0:
                finish_buffer_flag = True
                break
        if finish_buffer_flag:
            self.status = "post_handle"
            return finish_buffer_flag
        else:
            self.status = "handling_and_create"
            return finish_buffer_flag
        

    def postHandle(self):
        """后处理，一般是保存等细节。
        """
        self.test_fighting_data_logger.log()
        self.test_fighting_data_logger.list_log(lists=self.fighting_data_map_list)
        return True
    
    def end(self):
        self.elo_opponents.move(self.args)
        del self.elo_opponents
        del self.trainer
        gc.collect()

    def reset(self):
        self.status = "pre_handle"

    def next(self):
        """训练好的Agent放入测试中
        """
        # self.next.add_agent.remote(agent)
        if self.next_task != None:
            self.next_task.reset.remote()
        return self.next_task
