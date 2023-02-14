from Entity.Agent.rl_agent_factory import CreateAgent
from Entity.Elo.EloOpponents import EloOpponents
import myenv, gym, ray
import numpy as np

class ModelRollout:
    def __init__(self, model, step: int, EloOpponents: EloOpponents):
        self.model = model
        self.step = step
        self.elo_opponents = EloOpponents

@ray.remote(num_cpus=4)
class RolloutWorkerParallel():
    '''
    创建工人；打开环境；加载模型；从环境获取经验并返回经验
    '''
    def __init__(self, args, identifier):
        import myenv
        self.rolloutWorker = RolloutWorker(args, identifier)
        pass

    def rollout(self, model):
        return self.rolloutWorker.rollout(model)

    def close(self):
        self.rolloutWorker.close()

class RolloutWorker():
    def __init__(self, args, identifier, agent=None):
        self.env = gym.make(args["env"])
        if agent == None:
            self.agent = CreateAgent(env=self.env, args=args)
        else:
            self.agent = agent
        self.port = args["port"] + identifier
        self.p1_runner = {"name": args["agent_name"], "agent": self.agent}
        self.args = args
        np.random.seed(self.port)
        pass
    
    def close(self):
        self.agent.close()
        self.env.close()
        pass
    
    def _reset(self, model): 
        elo_opponents = model.elo_opponents
        p2_bot = elo_opponents.select_opponent(self.port)
        p1_flag = True if np.random.choice(2) == 0 else False
        return self.env.reset(p1_bot=self.p1_runner, p2_bot = p2_bot, character = self.args["character"], p1_flag = p1_flag, port=self.port)
    
    def rollout(self, model: ModelRollout):
        """ 样本采集器，可以添加模型

        Args:
            model (ModelRollout): 样本采集器

        Returns:
            buffer: 样本缓冲池
            csvList: 对战数据列表
            oppList: 对手更新Elo值列表
        """
        if model.model != None:
            self.agent.set_weights(model.model)
            
        o = self._reset(model)
        r, d, ep_ret, ep_len = 0, False, 0, 0

        csvList = []
        oppList = []
        t = 0
        info = self.env.info
        
        while t <= self.args["local_steps_per_epoch"]:
            a, v_t, logp_t = self.agent.inferAndCollectSample(o, info=info)

            o2, r, d, info2 = self.env.step(a)

            # print(info)
            # fightingice terminate when env timeout or one character is killed
            # there should be not max_ep_len
            terminal = d or (ep_len == self.args["max_ep_len"])
            if terminal or (t == self.args["local_steps_per_epoch"]):
                if not (terminal):
                    print('Warning: trajectory cut off by epoch at %d steps.' % ep_len)
                    t += 1
                # if trajectory didn't reach terminal state, bootstrap value target
                # last_val = 0 if d else sess.run(v, feed_dict={x_ph: o.reshape(1, -1)})
                # there is no terminal state in fightingice, always backup last normal state o value
                last_val = self.agent.inferV(o)
                self.agent.buf.finish_path(last_val)
                if terminal:
                    # only save EpRet / EpLen if trajectory finished
                    print("ep_len: {}".format(ep_len))
                    
                    # log opp elo
                    opp_list, csv_list = model.elo_opponents.log(self.env, model.step, ep_len, ep_ret)
                    oppList.append(opp_list)
                    csvList.append(csv_list)
                    
                    
                    o = self._reset(model)
                    info = self.env.info
                    ep_ret, ep_len = 0, 0
            else:
                ep_ret += r
                ep_len += 1
                # save and log
                self.agent.buf.store(o, a, r, v_t, logp_t, info=info)

                # Update obs (critical!)
                o = o2
                info = info2
                t += 1

        return self.agent.buf.get(), csvList, oppList