import time
from Entity.Agent.rl_agent_factory import CreateAgent
from Entity.Elo.EloOpponents import EloOpponents
import myenv, gym, ray
import numpy as np

class TaskRolloutWorker():
    def __init__(self, args, identifier, queue, agent=None):
        self.env = gym.make(args["env"])
        self.queue = queue
        if agent == None:
            self.agent = CreateAgent(env=self.env, args=args)
        else:
            self.agent = agent
        self.port = args["port"] + identifier
        self.args = args
        np.random.seed(self.port)
        pass
    
    def close(self):
        self.agent.close()
        self.env.close()
        pass
    
    def rollout(self):
        """ 样本采集器，可以添加模型

        Args:
            model (ModelRollout): 样本采集器

        Returns:
            buffer: 样本缓冲池
            csvList: 对战数据列表
            oppList: 对手更新Elo值列表
        """

        while True:
        # for _ in range(1):
            models = ray.get(self.queue.get(block=True))
            # print("zhongqian models: ")
            # print(type(models))
            
            step: int = models["step"]
            p1_flag: bool = models["p1_flag"]
            p2_bot: dict = models["p2_bot"] # ray.get(models["p2_bot"])
            p1_runner =  models["p1_runner"] # ray.get(models["p1_runner"])
            output_queue = models["output_queue"]
            task = models["task"]
            model = p1_runner["agent"].get_weights()
            
            if ray.get(task.compare_status.remote(step)) == False:
                continue

            # start_time = time.time()

            if model != None:
                self.agent.set_weights(model)
                
            # o = self._reset(model)
            o = self.env.reset(p1_bot=p1_runner, p2_bot = p2_bot, character = self.args["character"], p1_flag = p1_flag, port=self.port)
            r, d, ep_ret, ep_len = 0, False, 0, 0

            csvList = []
            oppList = []
            store_list = []
            t = 0
            info = self.env.info
            
            while True:
                a, v_t, logp_t = self.agent.inferAndCollectSample(o, info=info)

                o2, r, d, info2 = self.env.step(a)

                # print(info)
                # fightingice terminate when env timeout or one character is killed
                # there should be not max_ep_len
                terminal = d or (ep_len == self.args["max_ep_len"])
                if terminal:
                    # if trajectory didn't reach terminal state, bootstrap value target
                    # last_val = 0 if d else sess.run(v, feed_dict={x_ph: o.reshape(1, -1)})
                    # there is no terminal state in fightingice, always backup last normal state o value
                    last_val = self.agent.inferV(o)
                    # self.agent.buf.finish_path(last_val)
                    store_list.append(last_val)

                    # log opp elo
                    opp_list, csv_list = EloOpponents.log(p1_runner["name"], self.env, step, ep_len, ep_ret)
                    # oppList.append(opp_list)
                    # csvList.append(csv_list)
                    oppList = opp_list
                    csvList = csv_list
                    break
                else:
                    ep_ret += r
                    ep_len += 1
                    # save and log
                    # self.agent.buf.store(o, a, r, v_t, logp_t, info=info)
                    store_list.append({"o": o, "a": a, "r": r, "v_t": v_t, "logp_t": logp_t, "info": info})
                    # Update obs (critical!)
                    o = o2
                    info = info2
                    t += 1
            # if ray.get(task.compare_status.remote(step)) == False:
            #     continue
            output_queue.put({"store_list": store_list, "csv_list": csvList, "opp_list": oppList}, block=False)

            # print("——————————————Time required for this track: " + str(time.time() - start_time))
            

        # return self.agent.buf.get(), csvList, oppList