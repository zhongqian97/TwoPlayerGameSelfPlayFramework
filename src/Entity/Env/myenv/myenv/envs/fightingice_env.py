import os
import platform
import random
import subprocess
import time
from myenv.envs.ppo_ai import PpoAIFactory
import numpy
from multiprocessing import Pipe
from threading import Thread

import gym
from gym import error, spaces, utils
from gym.utils import seeding
from py4j.java_gateway import (CallbackServerParameters, GatewayParameters,
                               JavaGateway, get_field)

from Entity.Elo.EloOpponents import EloOpponents
from Entity.Utils.bark_log import bark_log


def game_thread(env):
    try:
        env.game_started = True
        env.manager.runGame(env.game_to_start)
    except:
        env.game_started = False
        print("Please IGNORE the Exception above because of restart java game")

class FightingiceEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, **kwargs):

        self.freq_restart_java = 1       # frequency of rounds to restart java env
        self.java_env_path = os.getcwd()
        self.java_env_path = './Entity/Env/FTG4.50/'
        if "java_env_path" in kwargs.keys():
            self.java_env_path = kwargs["java_env_path"]
        if "freq_restart_java" in kwargs.keys():
            self.freq_restart_java = kwargs["freq_restart_java"]
        if "port" in kwargs.keys():
            self.port = 4242
        else:
            try:
                # import port_for
                # self.port = port_for.select_random()  # select one random port for java env
                self.port = 4242
            except:
                raise ImportError(
                    "Pass port=[your_port] when make env, or install port_for to set startup port automatically, maybe pip install port_for can help")


        _actions = "AIR_A AIR_B AIR_D_DB_BA AIR_D_DB_BB AIR_D_DF_FA AIR_D_DF_FB AIR_DA AIR_DB AIR_F_D_DFA AIR_F_D_DFB AIR_FA AIR_FB AIR_UA AIR_UB BACK_JUMP BACK_STEP CROUCH_A CROUCH_B CROUCH_FA CROUCH_FB CROUCH_GUARD DASH FOR_JUMP FORWARD_WALK JUMP NEUTRAL STAND_A STAND_B STAND_D_DB_BA STAND_D_DB_BB STAND_D_DF_FA STAND_D_DF_FB STAND_D_DF_FC STAND_F_D_DFA STAND_F_D_DFB STAND_FA STAND_FB STAND_GUARD THROW_A THROW_B"
        action_strs = _actions.split(" ")    # 40 actions
        self.MASK = numpy.array([[1] * len(action_strs)])
        # # all valid opp ai bots
        # self.opp_ai_list = ["ERHEA_PI_DJL", "TeraThunder", "CYR_AI", "EmcmAi",
        #                     "BCP", "JayBot_GM", "SimpleAI",
        #                     "DiceAI", "KotlinTestAgent",
        #                     "Dora", "LGIST_Bot", "Toothless",
        #                     "FalzAI", "ReiwaThunder", "TOVOR",
        #                     "HaibuAI", "MctsAi", "UtalFighter"]
        # # , "MctsAi" , "ERHEA_PI_DJL", "JayBot_GM", "SimpleAI", "TeraThunder"
        # # ,"Thunder"
        #                     # ["JayBot_GM", "SimpleAI",
        #                     # "DiceAI", "KotlinTestAgent",
        #                     # "Dora", "LGIST_Bot",
        #                     # "FalzAI", "ReiwaThunder",
        #                     # "HaibuAI", "UtalFighter"]
        # # store opp elo rating
        # self.opp_elo_dict = {}
        # for opp in self.opp_ai_list:
        #     self.opp_elo_dict[opp] = 0
        # all characters
        # self.character_list = ["ZEN"] # ["ZEN", "GARNET", "LUD"]

        self.observation_space = spaces.Box(low=-1, high=1, shape=(144*3,))
        self.mask_space = spaces.Box(low=0, high=1, shape=(len(action_strs),))
        self.action_space = spaces.Discrete(len(action_strs))

        os_name = platform.system()
        if os_name.startswith("Linux"):
            self.system_name = "linux"
        elif os_name.startswith("Darwin"):
            self.system_name = "macos"
        else:
            self.system_name = "windows"

        if self.system_name == "linux":
            # first check java can be run, can only be used on Linux
            java_version = subprocess.check_output(
                'java -version 2>&1 | awk -F[\\\"_] \'NR==1{print $2}\'', shell=True)
            if java_version == b"\n":
                raise ModuleNotFoundError("Java is not installed")
        else:
            print("Please make sure you can run java if you see some error")

        # second check if FightingIce is installed correct
        start_jar_path = os.path.join(self.java_env_path, "FightingICE.jar") # FightingICE.jar ftg450.jar
        start_data_path = os.path.join(self.java_env_path, "data")
        start_lib_path = os.path.join(self.java_env_path, "lib")
        start_erhea_path = os.path.join(start_lib_path, "erheajar", "*")
        lwjgl_path = os.path.join(start_lib_path, "lwjgl", "*")
        lib_path = os.path.join(start_lib_path, "*")
        start_system_lib_path = os.path.join(
            self.java_env_path, "lib", "natives", self.system_name)
        natives_path = os.path.join(start_system_lib_path, "*")

        # if os.path.exists(start_jar_path) and os.path.exists(start_data_path) and os.path.exists(start_lib_path) and os.path.exists(start_system_lib_path):
        #     pass
        # else:
        #     error_message = "FightingICE is not installed in your script launched path {}, set path when make() or start script in FightingICE path".format(
        #         self.java_env_path)
        #     raise FileExistsError(error_message)
        
        self.java_ai_path = os.path.join(self.java_env_path, "data", "ai")
        ai_path = os.path.join(self.java_ai_path, "*")
        if self.system_name == "windows":
            self.start_up_str = "{};{};{};{};{};{}".format(
                start_jar_path, lwjgl_path, natives_path, lib_path, start_erhea_path, ai_path)
            self.need_set_memory_when_start = True
            
        else:
            self.start_up_str = "{}:{}:{}:{}:{}".format(
                start_jar_path, lwjgl_path, natives_path, lib_path, start_erhea_path) # , ai_path)
            self.need_set_memory_when_start = False
            

        self.game_started = False
        self.round_num = 0
        self.win = False
        self.p1_hp = -1
        self.p2_hp = -1
        self.frame = -1

    def theEnvIsEnd(self):
        if self.frame == 3600 or self.frame == 4200 or self.p1_hp == 0 or self.p2_hp == 0:
            return True
        else:
            return False

    def _start_java_game(self):
        # start game
        print("Start java env in {} and port {}".format(
            self.java_env_path, self.port))
        devnull = open(os.devnull, 'w')

        # if env_args is None:
        #     env_args = ["--fastmode", "--grey-bg", "--inverted-player", "1", "--mute", "--disable-window", "--limithp", "400", "400"]
        
        env_args = ["--fastmode", "--grey-bg", "--mute", "--limithp", "400", "400", "--disable-window", "--inverted-player", "1"]
        # env_args = ["--fastmode", "--grey-bg", "--mute", "--limithp", "400", "400"]

        # print("zhongqian 131:")
        # print(self.start_up_str)
        if self.system_name == "windows":
            # -Xms1024m -Xmx1024m we need set this in windows
            self.java_env = subprocess.Popen(["java", "-Xms1024m", "-Xmx1024m", "-cp", self.start_up_str, "Main",
                                              "--port", str(self.port), "--py4j"] + env_args, stdout=devnull, stderr=devnull)
        elif self.system_name == "linux":
            self.java_env = subprocess.Popen(["java", "-cp", self.start_up_str, "Main", "--port", str(self.port),
                                              "--py4j"] + env_args, stdout=devnull, stderr=devnull)
            pass
        elif self.system_name == "macos":
            self.java_env = subprocess.Popen(["java", "-XstartOnFirstThread", "-cp", self.start_up_str, "Main",
                                              "--port", str(self.port), "--py4j"] + env_args, stdout=devnull, stderr=devnull)
        # self.java_env = subprocess.Popen(["java", "-cp", self.start_up_str, #"FightingICE.jar:./lib/lwjgl/*:./lib/natives/linux/*:./lib/*",
        #      "Main", "--port", str(self.port), "--py4j", "--c1", "ZEN", "--c2", "ZEN","--fastmode", "--grey-bg", "--mute"])
        # sleep 3s for java starting, if your machine is slow, make it longer
        # print(self.java_env)
        time.sleep(3)

    def _start_gateway(self, p1_bot_agent=None, p2_bot_agent=None, p1_flag = True):
        """p1代表自己人

        Args:
            p1 (_type_, optional): _description_. Defaults to None.
            p2 (_type_, optional): _description_. Defaults to None.
        """
        # auto select callback server port and reset it in java env
        self.gateway = JavaGateway(gateway_parameters=GatewayParameters(
            port=self.port), callback_server_parameters=CallbackServerParameters(port=0))
        python_port = self.gateway.get_callback_server().get_listening_port()
        
        # 延迟10秒
        i = 0
        while i < 10:
            time.sleep(1)
            try:
                python_port = self.gateway.java_gateway_server.resetCallbackClient(
                    self.gateway.java_gateway_server.getCallbackClient().getAddress(), python_port)
                i = 10
            except Exception:
                i += 1
        
        self.manager = self.gateway.entry_point

        # create pipe between gym_env_api and python_ai for java env
        server, client = Pipe()
        self.pipe = server
#        self.p1 = GymAI(self.gateway, client, False)
        # self.p1 = PpoAI(self.gateway, client)
        # self.p1_name = self.p1.__class__.__name__
        p1_bot = PpoAIFactory(p1_bot_agent["name"], p1_bot_agent["agent"])
        self.p1 = p1_bot.getAgent(self.gateway, client)
        self.p1_name = p1_bot.name
        self.manager.registerAI(self.p1_name, self.p1)
        
        if isinstance(p2_bot_agent["agent"], str):
            # p2 is a java class name
            self.p2 = p2_bot_agent["agent"]
            self.p2_name = p2_bot_agent["name"]
        else:
            # p2 is a python class
            p2_bot = PpoAIFactory(p2_bot_agent["name"], p2_bot_agent["agent"])
            self.p2 = p2_bot.getAgent(self.gateway)
            # self.p2_name = self.p2.__class__.__name__
            self.p2_name = p2_bot.name
            self.manager.registerAI(self.p2_name, self.p2)

        if p1_flag == False:
            self.p1, self.p2 = self.p2, self.p1
            self.p1_name, self.p2_name = self.p2_name, self.p1_name
        # self.character = random.choice(self.character_list)
        
        self.game_to_start = self.manager.createGame(
            self.character, self.character, self.p1_name, self.p2_name, self.freq_restart_java)
        print("start fightingice env: {} vs {} in {}".format(self.p1_name, self.p2_name, self.character))

        self.game = Thread(target=game_thread,
                           name="game_thread", args=(self, ))
        self.game.start()

        self.game_started = True
        self.round_num = 0
        self.win = False
        self.p1_hp = -1
        self.p2_hp = -1
        self.frame = -1
        self.info = {}

    def _close_gateway(self):
        self.gateway.close_callback_server()
        self.gateway.close()
        del self.gateway

    def _close_java_game(self):
        self.java_env.kill()
        del self.java_env
        self.pipe.close()
        del self.pipe
        self.game_started = False
        time.sleep(3)

    # def reset(self, p1_bot = None, p2_bot = None, character = None, p1_flag = None, port: int = 0):
    #     while True:
    #         try:
    #             obs = self._reset(p1_bot = p1_bot, p2_bot = p2_bot, character = character, p1_flag = p1_flag, port = port)
    #             break
    #         except Exception as e:
    #             print(e)
    #             bark_log("Exception_def_reset")
    #     return obs
    
    def reset(self, p1_bot = None, p2_bot = None, character = None, p1_flag = None, port: int = 0):
        """_summary_

        Args:
            p1_bot (_type_, optional): _description_. Defaults to None.
            p2_bot (_type_, optional): _description_. Defaults to None.
            character (_type_, optional): _description_. Defaults to None.
            p1_flag (_type_, optional): _description_. 是否为1p，是1p为True。
            port (int, optional): _description_. Defaults to 0.

        Raises:
            SystemExit: _description_

        Returns:
            _type_: _description_
        """
        # 有则替换，无则替代    
        if port != 0:
            self.port = port   
              
        if p1_bot == None:
            p1_bot = self.p1_bot
        else:
            self.p1_bot = p1_bot
            
        if p2_bot == None:
            p2_bot = self.p2_bot
        else:
            self.p2_bot = p2_bot
        
        if character == None:
            character = self.character
        else:
            self.character = character
            
        if p1_flag == None:
            p1_flag = self.p1_flag
        else:
            self.p1_flag = p1_flag  
        
        # start java game if game is not started
        if self.game_started is False:
            try:
                self._close_gateway()
                self._close_java_game()
            except:
                pass
            self._start_java_game()
            # time.sleep(3)
            self._start_gateway(p1_bot, p2_bot, p1_flag)

        # to provide crash, restart java game in some freq
        if self.round_num >= self.freq_restart_java:
            try:
                self._close_gateway()
                self._close_java_game()
                self._start_java_game()
            except:
                raise SystemExit("Can not restart game")
            self._start_gateway(p1_bot, p2_bot, p1_flag)

        # just reset is anything ok
        self.pipe.send("reset")
        self.round_num += 1
        if self.pipe.poll(60):
            obs, mask = self.pipe.recv()
            self.info = {"mask": mask}
        else:
            print("fail in reset and let's do it again.")
            obs = self.reset()
        return obs

    # def step(self, action):
    #     while True:
    #         try:
    #             new_obs, new_mask, reward, done, info = self.steps(action)
    #             info["mask"] = new_mask
    #             break
    #         except Exception as e:
    #             print(e)
    #             bark_log("Exception_def_step")
    #     return new_obs, reward, done, info
    
    def step(self, action):
        # check if game is running, if not try restart
        # when restart, dict will contain crash info, agent should do something, it is a BUG in this version
        if self.game_started is False:
            dicts = {}
            dicts["pre_game_crashed"] = True
            obs = self.reset()
            dicts["mask"] = self.info["mask"]
            return obs, 0, None, dicts
        
        self.pipe.send(["step", action[0]])
        if self.pipe.poll(60):
            new_obs, new_mask, reward, done, info = self.pipe.recv()
            if info != None:
                info = eval(info)
                self.win = info['win']
                self.p1_hp = info['p1_hp']
                self.p2_hp = info['p2_hp']
                self.frame = info['frame']
            info["mask"] = new_mask
                 
        else:
            new_obs, reward, done, info = None, 0, True, None
            print("can't receive signals within 10 seconds. let's terminate gym env.")

        self.info["character"] = self.character
        self.info["p1"] = self.p1_name
        self.info["p2"] = self.p2_name
        self.info["p1_hp"] = self.p1_hp
        self.info["p2_hp"] = self.p2_hp
        self.info["isWin"] = self.win
        self.info["frame"] = self.frame
        return new_obs, reward, done, info

    def render(self, mode='human'):
        # no need
        pass

    def close(self):
        if self.game_started:
            try:
                self._close_gateway()
            except:
                pass
            self._close_java_game()


if __name__ == "__main__":
    env = FightingiceEnv()