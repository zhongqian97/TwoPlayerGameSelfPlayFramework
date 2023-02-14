from Entity.Agent.pytorch.ppg import PPGAgent
from Entity.Agent.pytorch.ppo import PPOAgent

import torch

def CreateAgent(args=None, env=None):
    if args["algorithm"] == 'PPO':
        return PPOAgent(args, env)
    elif args["algorithm"] == 'PPG':
        return PPGAgent(args, env)


# class RLAgent():
#     def __init__(self, args=None, env=None):
#         self.ac = None
#         pass
    
#     def max_model_id(self, file_dir):
#         import re, os
#         all_files = []
#         for root, dirs, files in os.walk(file_dir):
#             all_files = files

#         ids = []
#         for filename in all_files:
#             try:
#                 a = re.search('model\d*', filename).span()
#             except Exception:
#                 continue
#             ids.append(int(filename[5 + a[0]: a[1]]))
#         max_num = max(ids)
#         return 'model{}.pt'.format(max_num), max_num

#     def load(self, ai_name, file_path=None):
#         self.m_nStartEpoch = 1
#         import os.path as osp
#         if file_path == None:
#             self.checkpoints_dir = self.args["file_path"] + ai_name + '/'
#         else:
#             self.checkpoints_dir = file_path + ai_name + '/'
#         try:
#             file_name, m_nStartEpoch = self.max_model_id(self.checkpoints_dir)
#             actor_critic = torch.load(self.checkpoints_dir + file_name)
#             self.ac = actor_critic
#             self.m_nStartEpoch = m_nStartEpoch
#             print("load success.")
#         except Exception as e:
#             print("load model failed", e)
#             self.m_nStartEpoch = 1
#         return self.m_nStartEpoch

#     def close(self):
#         pass
    
#     def get_weights(self):
#         return self.ac
    
#     def set_weights(self, model):
#         self.ac = model
#         pass 
    
#     def save(self, epoch):
#         import os.path as osp
#         if epoch % self.save_freq == 0:
#             torch.save(self.ac, self.checkpoints_dir + "model" + str(epoch) + ".pt")
#         pass
    
#     def infer(self, o, info={}):
#         pass

#     def inferV(self, o):
#         pass
    
#     def inferAndCollectSample(self, o, info={}):
#         pass
            
#     def train(self, samples, step):
#         pass