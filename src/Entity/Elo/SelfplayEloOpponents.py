from Entity.Agent.rl_agent_factory import CreateAgent
from Entity.Elo.EloOpponents import EloOpponents

import os 

from Entity.Utils.bark_log import bark_log

class SelfplayEloOpponents(EloOpponents):
    def addSelfplayEloOpponent(self, args, env):
        """添加自博弈智能体到对手池中

        Args:
            args (_type_): 参数池
            env (_type_): 环境

        Returns:
            bool: 是否只有自己返回值，如只有自己，那还自博弈个锤子
        """
        if self.args["clean_buffer"] == "True":
            self.clean_buffer()
            print("self.clean_buffer()")
        ai_name_list = os.listdir(args["agent_file_path"])
        for ai_name in ai_name_list:
            if os.path.isdir(args["agent_file_path"] + ai_name) and self.name != ai_name:
                agent = CreateAgent(args, env)
                epoch = agent.load(ai_name, args["agent_file_path"])
                if epoch > 1:
                    # bark_log(ai_name)
                    self.add(ai_name, agent)
                # else:
                #     bark_log("else_agent_hasUse")
                
        if len(ai_name_list) == 0:
            return True
        return False

    def addSelfplayInSelf(self, args, env):
        """添加自身在不同时期的Agent
        """
        agent = CreateAgent(args, env)
        epoch = agent.load(args["agent_name"], args["agent_file_path"])
        # self.add(args["agent_name"] + "_" + str(epoch), agent)
        for i in range(epoch - args["iterations_test"], 0, -args["iterations_test"]):
            agent = CreateAgent(args, env)
            epoch = agent.load(args["agent_name"], args["agent_file_path"], model=i)
            self.add(args["agent_name"] + "_" + str(epoch), agent)

    def move(self, args):
        os.system("touch " + args["file_path"] + args["agent_name"] + '/Done')
        if self.args['if_open_selfplay'] == "True":
            os.system("cp -r " + args["file_path"] + args["agent_name"] + " " + args["agent_file_path"])
