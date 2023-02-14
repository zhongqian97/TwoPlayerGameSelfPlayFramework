from ast import Try
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
from Entity.Utils.config import FrameConfig, create_agent
from Entity.Agent.rl_agent_factory import CreateAgent
import gc
import gym
import myenv
import numpy as np
import os

@ray.remote(num_cpus=1)
class TrainTask(ATask):
    def __init__(self, args, fastmode=True) -> None:
        super().__init__()
        self.args = args
        self.queue = Queue()
        self.status = "pre_handle"
        self.queue_clear = None
        self.fastmode = fastmode
        self.the_one_mode = (fastmode == False)
        self.elo_opponents = None

    def set_self_and_next(self, self_task, next_task):
        self.self_task = self_task
        self.next_task = next_task

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

        elif self.status == "pre_handle_the_one":
            self.preHandleTheOne()
            self.status = "handling_and_create"
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
                self.iterations += 1
            else:
                self.status = "handling_and_create"
                self.iterations += 1
                if self.fastmode and self.args["max_epochs"] < self.iterations:
                    self.status = "end"
                self._init()
                
        elif self.status == "end":
            self.end()
            pass
        pass
        
    def preHandleTheOne(self):
        import myenv
        env = gym.make(self.args["env"])

        self.elo_opponents.addSelfplayEloOpponent(self.args, env)
        self.elo_opponents.addSelfplayInSelf(self.args, env)
        self.elo_opponents_logger.log_append(self.elo_opponents.opp_ai_list)
        self.winrate_opponents_logger.log_append(self.elo_opponents.opp_ai_list)

        env.close()
        pass

    def preHandle(self):
        """从零开始做训练，这里主要用于训练前的文件夹创建的等等。
        """
        import myenv
        self.args = FrameConfig(self.args)
        if self.fastmode:
            self.agent_name = self.args["agent_name"]
        else:
            self.agent_name = self.args["agents_name"][:-1]
            self.args["agent_name"] = self.agent_name
            create_agent(self.args, self.agent_name)

        env = gym.make(self.args["env"])
        self.trainer = CreateAgent(args=self.args, env=env)
        if self.elo_opponents == None:
            self.elo_opponents = SelfplayEloOpponents(self.args)
        else:
            self.elo_opponents.init(self.args)
        self.elo_opponents.addSelfplayEloOpponent(self.args, env)
        if self.fastmode == False:
            self.elo_opponents.addSelfplayInSelf(self.args, env)

        self.fighting_data_logger = Logger(
            self.args["file_path"] + self.agent_name + self.args["fighting_data_file_path"], self.args["fighting_data_csv"])
        self.train_variable_logger = Logger(
            self.args["file_path"] + self.agent_name + self.args["train_variable_file_path"], self.trainer.train_maps_list)
        self.elo_opponents_logger = Logger(
            self.args["file_path"] + self.agent_name + self.args["elo_opponents_file_path"], self.elo_opponents.opp_ai_list)
        self.winrate_opponents_logger = Logger(
            self.args["file_path"] + self.agent_name + self.args["winrate_opponents_file_path"], self.elo_opponents.opp_ai_list)

        self.elo_opponents.load(self.agent_name)
        self.start_epoch = self.trainer.load(self.agent_name)

        if self.start_epoch == 1:
            self.fighting_data_logger.log()
            self.train_variable_logger.log()
            self.elo_opponents_logger.log()
            self.winrate_opponents_logger.log()
        else:
            self.start_epoch += 1
        env.close()
        pass

    def create(self):
        """创建内容使用，Opponent choose在这里使用。
        """
        models = {}
        models["step"] = self.iterations
        models["p1_flag"] = True if np.random.choice(2) == 0 else False
        models["p2_bot"] = self.elo_opponents.select_opponent()
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
        return (step == self.iterations) and self.status == "handling_and_create"

    def handling(self):
        """放入buffer，并处理训练前的细节。
        首先将信息放入buffer中，
        """
        # self.status = "handling_no_create"
        finish_buffer_flag = False
        while self.queue.empty() == False:
            trajectory = self.queue.get()
            store_list = trajectory["store_list"]
            fighting_data_map = trajectory["csv_list"]
            opp_list = trajectory["opp_list"]

            if fighting_data_map["epoch"] != self.iterations:
                continue
            
            if self.trainer.train_buf.full():
                self.queue_clear = self.queue.get_nowait_batch(self.queue.size())
                finish_buffer_flag = True
                break

            for i in range(len(store_list) - 1):
                store = store_list[i]
                self.trainer.train_buf.store(store["o"], store["a"], store["r"], store["v_t"], store["logp_t"], store["info"])
                if self.trainer.train_buf.full():
                    self.queue_clear = self.queue.get_nowait_batch(self.queue.size())
                    finish_buffer_flag = True
                    
                    if i == len(store_list) - 2:
                        self.trainer.train_buf.finish_path(store_list[len(store_list) - 1])
                    else:
                        self.trainer.train_buf.finish_path(self.trainer.inferV(store_list[i + 1]["o"]))
                    break

            self.opp_elo_list.append(copy.deepcopy(opp_list))
            self.fighting_data_map_list.append(copy.deepcopy(fighting_data_map))
            # trajectory
        if finish_buffer_flag:
            self.status = "post_handle"
            return finish_buffer_flag
        else:
            self.status = "handling_and_create"
            return finish_buffer_flag
        

    def postHandle(self):
        """后处理，一般是训练等细节。
        """
        self.elo_opponents.updateOppElo(self.opp_elo_list)
        self.train_variable_logger.log(maps=self.trainer.train(self.trainer.train_buf.get_and_use(), self.iterations))
        self.fighting_data_logger.list_log(lists=self.fighting_data_map_list)
        self.elo_opponents_logger.log(maps=self.elo_opponents.getOppDict())
        self.winrate_opponents_logger.log(maps=self.elo_opponents.getWinrateDict())

        self.trainer.save(self.iterations)
        self.elo_opponents.save()
        if self.fastmode:
            return self.elo_opponents.theEnd()
        else:
            return self.iterations % self.args["iterations_test"] == 0
    
    def end(self):
        # self.elo_opponents.move(self.args)
        gc.collect()
        pass

    def reset(self):
        if self.fastmode:
            self.status = "pre_handle"
        else:
            self.status = "pre_handle_the_one"

    def next(self):
        """训练好的Agent放入测试中
        """
        # self.next.add_agent.remote(agent)
        # self.status = "pre_handle"
        self.next_task.reset.remote()
        self.next_task.set_args.remote(ray.put(self.args))
        ray.get(self.next_task.set_elo_opponents.remote(ray.put(self.elo_opponents)))
        return self.next_task
