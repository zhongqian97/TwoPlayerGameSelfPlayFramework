from myenv.envs.SelfplayAgent import SelfplayAgent
import numpy as np
from py4j.java_gateway import get_field
from collections import deque

class PpoAI(object):
    """自博弈智能体创建

    Args:
        object (_type_): _description_
    """
    def __init__(self, gateway=None, pipe=None):
        self.gateway = gateway
        self.pipe = pipe
        
        self.width = 96  # The width of the display to obtain
        self.height = 64  # The height of the display to obtain
        self.grayscale = True  # The display's color to obtain true for grayscale, false for RGB

        self.obs = None
        self.just_inited = True

        self._actions = "AIR_A AIR_B AIR_D_DB_BA AIR_D_DB_BB AIR_D_DF_FA AIR_D_DF_FB AIR_DA AIR_DB AIR_F_D_DFA AIR_F_D_DFB AIR_FA AIR_FB AIR_UA AIR_UB BACK_JUMP BACK_STEP CROUCH_A CROUCH_B CROUCH_FA CROUCH_FB CROUCH_GUARD DASH FOR_JUMP FORWARD_WALK JUMP NEUTRAL STAND_A STAND_B STAND_D_DB_BA STAND_D_DB_BB STAND_D_DF_FA STAND_D_DF_FB STAND_D_DF_FC STAND_F_D_DFA STAND_F_D_DFB STAND_FA STAND_FB STAND_GUARD THROW_A THROW_B"
        self.action_strs = self._actions.split(" ")
        self.all_actions_mask =    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        self.air_actions_mask =    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.ground_actions_mask = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]

        self.pre_framedata = None
        self.skipping_frame = 12
        
    def init(self, gateway=None, pipe=None):
        if gateway != None:
            self.gateway = gateway
        if pipe != None:
            self.pipe = pipe

    def close(self):
        pass

    def initialize(self, gameData, player):
        self.inputKey = self.gateway.jvm.struct.Key()
        self.frameData = self.gateway.jvm.struct.FrameData()
        self.cc = self.gateway.jvm.aiinterface.CommandCenter()

        self.player = player
        self.gameData = gameData

        self.commands_in_delays = deque()
        self.jvm_actions = (self.gateway.jvm.enumerate.Action.AIR_A, self.gateway.jvm.enumerate.Action.AIR_B, self.gateway.jvm.enumerate.Action.AIR_D_DB_BA, self.gateway.jvm.enumerate.Action.AIR_D_DB_BB, self.gateway.jvm.enumerate.Action.AIR_D_DF_FA, self.gateway.jvm.enumerate.Action.AIR_D_DF_FB, self.gateway.jvm.enumerate.Action.AIR_DA, self.gateway.jvm.enumerate.Action.AIR_DB, self.gateway.jvm.enumerate.Action.AIR_F_D_DFA, self.gateway.jvm.enumerate.Action.AIR_F_D_DFB, self.gateway.jvm.enumerate.Action.AIR_FA, self.gateway.jvm.enumerate.Action.AIR_FB, self.gateway.jvm.enumerate.Action.AIR_UA, self.gateway.jvm.enumerate.Action.AIR_UB, self.gateway.jvm.enumerate.Action.BACK_JUMP, self.gateway.jvm.enumerate.Action.BACK_STEP, self.gateway.jvm.enumerate.Action.CROUCH_A, self.gateway.jvm.enumerate.Action.CROUCH_B, self.gateway.jvm.enumerate.Action.CROUCH_FA, self.gateway.jvm.enumerate.Action.CROUCH_FB, self.gateway.jvm.enumerate.Action.CROUCH_GUARD, self.gateway.jvm.enumerate.Action.DASH, self.gateway.jvm.enumerate.Action.FOR_JUMP, self.gateway.jvm.enumerate.Action.FORWARD_WALK, self.gateway.jvm.enumerate.Action.JUMP, self.gateway.jvm.enumerate.Action.NEUTRAL, self.gateway.jvm.enumerate.Action.STAND_A, self.gateway.jvm.enumerate.Action.STAND_B, self.gateway.jvm.enumerate.Action.STAND_D_DB_BA, self.gateway.jvm.enumerate.Action.STAND_D_DB_BB, self.gateway.jvm.enumerate.Action.STAND_D_DF_FA, self.gateway.jvm.enumerate.Action.STAND_D_DF_FB, self.gateway.jvm.enumerate.Action.STAND_D_DF_FC, self.gateway.jvm.enumerate.Action.STAND_F_D_DFA, self.gateway.jvm.enumerate.Action.STAND_F_D_DFB, self.gateway.jvm.enumerate.Action.STAND_FA, self.gateway.jvm.enumerate.Action.STAND_FB, self.gateway.jvm.enumerate.Action.STAND_GUARD, self.gateway.jvm.enumerate.Action.THROW_A, self.gateway.jvm.enumerate.Action.THROW_B)
        self.simulator = self.gameData.getSimulator()
        self.motions = self.gameData.getMotionData(self.player)
        self.motions_energy = []
        for i in range(len(self.action_strs)):
            # negative value
            self.motions_energy.append(self.motions.get(self.jvm_actions[i].ordinal()).getAttackStartAddEnergy())

        self.frozen_frames = 0
        self.framedata_deque = deque(maxlen=25)

        return 0

    # please define this method when you use FightingICE version 3.20 or later
    def roundEnd(self, x, y, z):
        # print("send round end to {}".format(self.pipe))
        # tell gym the env terminates
        if self.player:
            win = (x > y)
        else:
            win = (x < y)
        
        info = {}
        info['win'] = win
        info['p1_hp'] = x
        info['p2_hp'] = y
        info['frame'] = z
        
        self.pipe.send([None, None, 0, True, str(info)])
        self.just_inited = True
        # request = self.pipe.recv()
        # if request == "close":
        #     return
        self.obs = None
        self.frozen_frames = 0
        self.pre_framedata = None

        self.commands_in_delays.clear()
        self.framedata_deque.clear()
        self.inputKey.empty()
        self.cc.skillCancel()

    # Please define this method when you use FightingICE version 4.00 or later
    def getScreenData(self, sd):
        self.screenData = sd

    def getInformation(self, frameData, isControl):
#        self.pre_framedata = frameData if self.pre_framedata is None else self.frameData
        self.frameData = frameData
        self.isControl = isControl
        self.cc.setFrameData(self.frameData, self.player)
        if frameData.getEmptyFlag():
            return

    def input(self):
        return self.inputKey

    def gameEnd(self):
        pass

    def processing(self):
        ## game starts but round not start
        if self.frameData.getEmptyFlag() or self.frameData.getRemainingTime() <= 0:
            self.isGameJustStarted = True
            return

        if not self.isGameJustStarted:
            # totally start the round
            pass
            # Simulate the delay and look ahead 2 frames. The simulator class exists already in FightingICE
            # self.frameData = self.simulator.simulate(self.frameData, self.player, None, None, 17)
            # You can pass actions to the simulator by writing as follows:
            # actions = self.gateway.jvm.java.util.ArrayDeque()
            # actions.add(self.gateway.jvm.enumerate.Action.STAND_A)
            # self.frameData = self.simulator.simulate(self.frameData, self.player, actions, actions, 17)
        else:
            # If the game just started, no point on simulating
            self.isGameJustStarted = False

        ## store framedata for getObs()
        if self.frameData.getFramesNumber() == 0:
            for i in range(25):
                self.framedata_deque.append(self.frameData)
        else:
            self.framedata_deque.append(self.frameData)

        ## wait for frozen frame (Neutral command)
        if self.frozen_frames > 0:
            self.frozen_frames -= 1
            return
        # continue unfinished commands
        if self.cc.getSkillFlag():
            self.inputKey = self.cc.getSkillKey()
            return
        # wait for controllability
        if not self.isControl:
            return

        self.inputKey.empty()
        self.cc.skillCancel()

        delayed_frame = self.frameData.getFramesNumber()
        current_frame = delayed_frame + 15

        ## predict current framedata
        current_framedata = self.predict_current_framedata()

        ## action mask
        # air/ground according to predicted framedata,
        is_current_air = current_framedata.getCharacter(self.player).getState().equals(self.gateway.jvm.enumerate.State.AIR)
        action_mask = self.air_actions_mask if is_current_air else self.ground_actions_mask
        # mask energy actions according to delayed framedata
        action_mask = self.mask_energy_action(self.frameData.getCharacter(self.player).getEnergy(), action_mask)
        action_mask = np.array(action_mask)

        ## prepare state for gym policy
        # if just inited, should wait for first reset()
        if self.just_inited:
            request = self.pipe.recv()
            if request == "reset":
                self.just_inited = False
                self.obs = self.get_obs()
                self.pre_framedata = self.frameData
                self.pipe.send([self.obs, action_mask])
            else:
                # raise ValueError
                return
        # if not just inited but self.obs is none, it means second/thrid round just started
        # should return only obs for reset()
        elif self.obs is None:
            self.obs = self.get_obs()
            self.pre_framedata = self.frameData
            self.pipe.send([self.obs, action_mask])
        # if there is self.obs, do step() and return [obs, reward, done, info]
        else:
            self.obs = self.get_obs()
            self.reward = self.get_reward()
            self.pre_framedata = self.frameData
            win = (self.frameData.getCharacter(self.player).getHp()
                   > self.frameData.getCharacter(not self.player).getHp())
            info = {}
            info['win'] = win
            info['p1_hp'] = self.frameData.getCharacter(True).getHp()
            info['p2_hp'] = self.frameData.getCharacter(False).getHp()
            info['frame'] = self.frameData.getFramesNumber()
            self.pipe.send([self.obs, action_mask, self.reward, False, str(info)])

        ## receive action from gym
        #print("waitting for step in {}".format(self.pipe))
        request = self.pipe.recv()
        #print("get step in {}".format(self.pipe))
        if len(request) == 2 and request[0] == "step":
            action = request[1]
            command = self.action_strs[action]
            if command == "NEUTRAL":
                self.frozen_frames = 6
            else:
                self.frozen_frames = 0
                if command == "CROUCH_GUARD":
                    command = "1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1"
                elif command == "STAND_GUARD":
                    command = "4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4"
                self.cc.commandCall(command)
                self.commands_in_delays.append((current_frame, self.jvm_actions[action]))
                self.inputKey = self.cc.getSkillKey()




    def predict_current_framedata(self):
        ## remove old issued commands
        while (len(self.commands_in_delays) > 0 and
               self.commands_in_delays[0][0] < self.frameData.getFramesNumber()):
            self.commands_in_delays.popleft()

        ## simulate undelayed framedata with simulator and commands in delays
        simulate_framedata = self.frameData
        simulate_command = None
        simulate_frame = self.frameData.getFramesNumber()
        for waiting_frame, waiting_command in self.commands_in_delays:
            actions = self.gateway.jvm.java.util.ArrayDeque()
            if simulate_command is not None:
                actions.add(simulate_command)

            simulate_framedata = self.simulator.simulate(simulate_framedata, self.player, actions, None,
                                                         waiting_frame - simulate_frame)
            simulate_frame = waiting_frame
            simulate_command = waiting_command

        current_frame = self.frameData.getFramesNumber() + 15
        if current_frame > simulate_frame:
            actions = self.gateway.jvm.java.util.ArrayDeque()
            if simulate_command is not None:
                actions.add(simulate_command)
            simulate_framedata = self.simulator.simulate(simulate_framedata, self.player, actions, None,
                                                         current_frame - simulate_frame)

        # check if simulate framedata is correct, if not just assume not commands in delays
        if simulate_framedata.getCharacter(self.player).isControl() != self.isControl:
            simulate_framedata = self.simulator.simulate(self.frameData, self.player, None, None, 15)

        return simulate_framedata


    def mask_energy_action(self, energy, mask):
        energy_mask = []
        for i in range(len(self.action_strs)):
            if mask[i] == 0:
                energy_mask.append(0)
            elif self.motions_energy[i]+energy >= 0:
                energy_mask.append(1)
            else:
                energy_mask.append(0)
        return energy_mask


    def get_reward(self):
        try:
            if self.pre_framedata.getEmptyFlag() or self.frameData.getEmptyFlag():
                reward = 0
            else:
                p2_hp_pre = self.pre_framedata.getCharacter(False).getHp()
                p1_hp_pre = self.pre_framedata.getCharacter(True).getHp()
                p2_hp_now = self.frameData.getCharacter(False).getHp()
                p1_hp_now = self.frameData.getCharacter(True).getHp()
                x_dist_pre = self.pre_framedata.getDistanceX()
                x_dist_now = self.frameData.getDistanceX()
                if self.player:
                    reward = ((p2_hp_pre-p2_hp_now) - (p1_hp_pre-p1_hp_now)) / 10
                else:
                    reward = ((p1_hp_pre-p1_hp_now) - (p2_hp_pre-p2_hp_now)) / 10
                # if x_dist_now < x_dist_pre:
                #     bonus = +0.01
                # elif x_dist_now > x_dist_pre:
                #     bonus = -0.01
                # else:
                #     bonus = 0
                # reward += bonus
        except:
            reward = 0
        return reward

    def get_obs(self):
        def _get_obs(framedata, player):
            my = framedata.getCharacter(player)
            opp = framedata.getCharacter(not player)

            # my information
            myEnergy = my.getEnergy() / 300
            myX = ((my.getLeft() + my.getRight()) / 2 - 960/2) / (960/2)
            myY = ((my.getBottom() + my.getTop()) / 2) / 640
            mySpeedX = my.getSpeedX() / 20
            mySpeedY = my.getSpeedY() / 28
            myState = my.getState().ordinal()
            myAction = my.getAction().ordinal()
            myRemainingFrame = my.getRemainingFrame() / 70

            # opp information
            oppEnergy = opp.getEnergy() / 300
            oppX = ((opp.getLeft() + opp.getRight()) / 2 - (my.getLeft() + my.getRight()) / 2) / 960
            oppY = ((opp.getBottom() + opp.getTop()) / 2) / 640
            oppSpeedX = opp.getSpeedX() / 20
            oppSpeedY = opp.getSpeedY() / 28
            oppState = opp.getState().ordinal()
            oppAction = opp.getAction().ordinal()
            oppRemainingFrame = opp.getRemainingFrame() / 70

            observation = []

            # my information
            observation.append(myEnergy)        # [0,1]
            observation.append(myX)             # [-1,1]
            observation.append(myY)             # [0,1]
            observation.append(mySpeedX)        # [-1,1]
            observation.append(mySpeedY)        # [-1,1]
            for i in range(4):
                if i == myState:                # [0,1]
                    observation.append(1)
                else:
                    observation.append(0)
            for i in range(56):
                if i == myAction:               # [0,1]
                    observation.append(1)
                else:
                    observation.append(0)
            observation.append(myRemainingFrame)    # [0,1]

            # opp information
            observation.append(oppEnergy)       # [0,1]
            observation.append(oppX)            # [-1,1]
            observation.append(oppY)            # [0,1]
            observation.append(oppSpeedX)       # [-1,1]
            observation.append(oppSpeedY)       # [-1,1]
            for i in range(4):
                if i == oppState:           # [0,1]
                    observation.append(1)
                else:
                    observation.append(0)
            for i in range(56):
                if i == oppAction:          # [0,1]
                    observation.append(1)
                else:
                    observation.append(0)
            observation.append(oppRemainingFrame)   # [0,1]

            if player:
                myProjectiles = framedata.getProjectilesByP1()
                oppProjectiles = framedata.getProjectilesByP2()
            else:
                myProjectiles = framedata.getProjectilesByP2()
                oppProjectiles = framedata.getProjectilesByP1()

            if len(myProjectiles) == 2:
                myHitDamage = myProjectiles[0].getHitDamage() / 200.0
                myHitAreaNowX = ((myProjectiles[0].getCurrentHitArea().getLeft() + myProjectiles[
                    0].getCurrentHitArea().getRight()) / 2 - (my.getLeft() + my.getRight()) / 2) / 960.0
                myHitAreaNowY = ((myProjectiles[0].getCurrentHitArea().getTop() + myProjectiles[
                    0].getCurrentHitArea().getBottom()) / 2) / 640.0
                observation.append(myHitDamage)         # [0,1]
                observation.append(myHitAreaNowX)       # [-1,1]
                observation.append(myHitAreaNowY)       # [0,1]
                myHitDamage = myProjectiles[1].getHitDamage() / 200.0
                myHitAreaNowX = ((myProjectiles[1].getCurrentHitArea().getLeft() + myProjectiles[
                    1].getCurrentHitArea().getRight()) / 2 - (my.getLeft() + my.getRight()) / 2) / 960.0
                myHitAreaNowY = ((myProjectiles[1].getCurrentHitArea().getTop() + myProjectiles[
                    1].getCurrentHitArea().getBottom()) / 2) / 640.0
                observation.append(myHitDamage)
                observation.append(myHitAreaNowX)
                observation.append(myHitAreaNowY)
            elif len(myProjectiles) == 1:
                myHitDamage = myProjectiles[0].getHitDamage() / 200.0
                myHitAreaNowX = ((myProjectiles[0].getCurrentHitArea().getLeft() + myProjectiles[
                    0].getCurrentHitArea().getRight()) / 2 - (my.getLeft() + my.getRight()) / 2) / 960.0
                myHitAreaNowY = ((myProjectiles[0].getCurrentHitArea().getTop() + myProjectiles[
                    0].getCurrentHitArea().getBottom()) / 2) / 640.0
                observation.append(myHitDamage)
                observation.append(myHitAreaNowX)
                observation.append(myHitAreaNowY)
                for t in range(3):
                    observation.append(0.0)
            else:
                for t in range(6):
                    observation.append(0.0)

            if len(oppProjectiles) == 2:
                oppHitDamage = oppProjectiles[0].getHitDamage() / 200.0
                oppHitAreaNowX = ((oppProjectiles[0].getCurrentHitArea().getLeft() + oppProjectiles[
                    0].getCurrentHitArea().getRight()) / 2 - (my.getLeft() + my.getRight()) / 2) / 960.0
                oppHitAreaNowY = ((oppProjectiles[0].getCurrentHitArea().getTop() + oppProjectiles[
                    0].getCurrentHitArea().getBottom()) / 2) / 640.0
                observation.append(oppHitDamage)
                observation.append(oppHitAreaNowX)
                observation.append(oppHitAreaNowY)
                oppHitDamage = oppProjectiles[1].getHitDamage() / 200.0
                oppHitAreaNowX = ((oppProjectiles[1].getCurrentHitArea().getLeft() + oppProjectiles[
                    1].getCurrentHitArea().getRight()) / 2 - (my.getLeft() + my.getRight()) / 2) / 960.0
                oppHitAreaNowY = ((oppProjectiles[1].getCurrentHitArea().getTop() + oppProjectiles[
                    1].getCurrentHitArea().getBottom()) / 2) / 640.0
                observation.append(oppHitDamage)
                observation.append(oppHitAreaNowX)
                observation.append(oppHitAreaNowY)
            elif len(oppProjectiles) == 1:
                oppHitDamage = oppProjectiles[0].getHitDamage() / 200.0
                oppHitAreaNowX = ((oppProjectiles[0].getCurrentHitArea().getLeft() + oppProjectiles[
                    0].getCurrentHitArea().getRight()) / 2 - (my.getLeft() + my.getRight()) / 2) / 960.0
                oppHitAreaNowY = ((oppProjectiles[0].getCurrentHitArea().getTop() + oppProjectiles[
                    0].getCurrentHitArea().getBottom()) / 2) / 640.0
                observation.append(oppHitDamage)
                observation.append(oppHitAreaNowX)
                observation.append(oppHitAreaNowY)
                for t in range(3):
                    observation.append(0.0)
            else:
                for t in range(6):
                    observation.append(0.0)

            return observation            # 144

        observations = []
        observations.extend(_get_obs(self.framedata_deque[-1], self.player))
        observations.extend(_get_obs(self.framedata_deque[-1-12], self.player))
        observations.extend(_get_obs(self.framedata_deque[-1-24], self.player))

        observations = np.array(observations, dtype=np.float32)
        observations = np.clip(observations, -1, 1)
        return observations

    # This part is mandatory
    class Java:
        implements = ["aiinterface.AIInterface"]

class PpoAIFactory():
    
    def __init__(self, name, agent: PpoAI = None):
        self.name = name
        self.agent = agent
        pass
    
    def getAgent(self, gateway, pipe=None):
        if pipe == None:
            return PpoAI(gateway, SelfplayAgent(self.agent))
        else:
            return PpoAI(gateway, pipe)
        