from Entity.Agent.rl_agent_factory import CreateAgent

from Entity.Elo.EloOpponents import EloOpponents
import myenv, gym, ray, time
import numpy as np

from Entity.Utils.bark_log import bark_log

@ray.remote(num_cpus=4)
class TestWorkerParallel():
    '''
    创建工人；打开环境；加载模型；从环境获取经验并返回经验
    '''
    def __init__(self, args, identifier, input_queue, output_queue, elo_opponents, model):
        import myenv
        self.testWorker = TestWorker(args, identifier, input_queue, output_queue, elo_opponents, model)
        pass

    def testing(self, input_queue):
        return self.testWorker.testing(input_queue)

    def close(self):
        self.testWorker.close()
        
class TestWorker():
    def __init__(self, args, identifier, input_queue, output_queue, elo_opponents, model, agent=None):
        self.env = gym.make(args["env"])
        if agent == None:
            self.agent = CreateAgent(env=self.env, args=args)
        else:
            self.agent = agent
        self.port = args["port"] + identifier
        self.p1_runner = {"name": args["agent_name"], "agent": self.agent}
        self.args = args
        self.input_queue, self.output_queue = input_queue, output_queue
        self.elo_opponents = elo_opponents
        self.agent.set_weights(model)
        pass
    
    def close(self):
        self.agent.close()
        self.env.close()
        pass
    
    def _reset(self):
        return self.env.reset(p1_bot=self.p1_runner, p2_bot = self.p2_bot, character = self.args["character"], p1_flag = self.p1_flag, port=self.port), self.env.info

    
    def testing(self, input_queue):
        output_queue = []
        while (len(input_queue) > 0):
            input_info = input_queue.pop()
            self.p2_bot = input_info["p2_bot"]
            self.p1_flag = input_info["p1_flag"]
            try:
                epoch = input_info["epoch"]
            except Exception:
                epoch = "test"
            test_round = 0
            while test_round < 1:
                o, info = self._reset()
                r, d, ep_ret, ep_len = 0, False, 0, 0
                fighting_data_map_list = []
                
                while True:
                    a = self.agent.infer(o, info=info)
                    o, r, d, info = self.env.step(a)
                    terminal = d
                    if terminal:
                        if self.env.theEnvIsEnd():
                            test_round += 1
                            # only save EpRet / EpLen if trajectory finished
                            print("ep_len: {}".format(ep_len))
                            _, fighting_data_map = self.elo_opponents.log(self.env, epoch, ep_len, ep_ret)
                            fighting_data_map_list.append(fighting_data_map)
                        if test_round >= 1:
                            break
                        o, info = self._reset()
                        ep_ret, ep_len = 0, 0
                    else:
                        ep_ret += r
                        ep_len += 1
                    pass
                pass
            
            info = {}
            # info["p1"] = self.args["agent_name"]
            info["p2_bot"] = self.p2_bot
            info["p1_flag"] = self.p1_flag
            # info["character"] = self.args["character"]
            info["fighting_data_map_list"] = fighting_data_map_list
            
            output_queue.append(info)
            # output_queue.extend(fighting_data_map_list)
        # bark_log(self.p2_bot + "_OOO_" + str(self.p1_flag))
        return output_queue
    
    