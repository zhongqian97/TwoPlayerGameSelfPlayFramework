import numpy as np
import torch
from torch.optim import Adam
import time
import Entity.Agent.pytorch.core as core
from Entity.Agent.pytorch.ppg_buffer import PpgAuxBuffer
from Entity.Agent.pytorch.ppo import PPOAgent
from Entity.Agent.pytorch.ppo_buffer import PPOBuffer
import torch.nn.functional as F

class PPGAgent(PPOAgent):
    def __init__(self, args=None, env=None):
        super().__init__(args, env)
        self.train_maps_list = ["step", "kl", "ent", "train_pi_iter", "train_aux_iter", "pi_l_old", "v_l_old", "pi_l_new", "v_l_new",
            "cf", "pi_l_new - pi_l_old", "v_l_new - v_l_old", "end_time - start_time"]
        self.aux_buffer = PpgAuxBuffer()
        self.value_clip = self.args["value_clip"]

    def _clipped_value_loss(self, values, rewards, old_values, clip):
        value_clipped = old_values + (values - old_values).clamp(-clip, clip)
        value_loss_1 = (value_clipped.flatten() - rewards) ** 2
        value_loss_2 = (values.flatten() - rewards) ** 2
        return torch.mean(torch.max(value_loss_1, value_loss_2))

    def train(self, samples, step):
        self.aux_buffer.put(samples)
        train_maps = super().train(samples, step)
        if step % self.args["num_policy_updates_per_aux"] != 0:
            train_maps["train_aux_iter"] = 0
            return train_maps

        data = self.aux_buffer.get()
        obs, mask, val, ret, act = data['obs'], data['mask'], data['val'], data['ret'], data['act']
        rewards = ret
        old_values = val
        logp_old = data['logp']


        # # get old action predictions for minimizing kl divergence and clipping respectively
        # old_action_probs, _ = self.actor(states)
        # old_action_probs.detach_()
        pi, logp_old = self.ac.pi(obs, mask=mask, act=act)
        old_action_probs = self.ac.pi.logits_mask
        old_action_probs.detach_()

        train_aux_iter = self.args["train_aux_iters"]
        # Train aux
        for epoch in range(self.args["train_aux_iters"]):
            self.pi_optimizer.zero_grad()

            # action_probs, policy_values = self.actor(states)
            # action_logprobs = action_probs.log()
            pi, logp = self.ac.pi(obs, mask=mask, act=act)

            approx_kl = (logp_old - logp).mean().item()
            kl = np.average(approx_kl)
            if kl > 1.5 * self.target_kl:
                train_aux_iter = epoch
                break

            action_probs, policy_values = self.ac.pi.logits_mask, self.ac.pi.value
            action_logprobs = action_probs.log()   
            policy_values = policy_values.flatten()        

            # policy network loss copmoses of both the kl div loss as well as the auxiliary loss
            aux_loss = self._clipped_value_loss(policy_values, rewards, old_values, self.value_clip)
            loss_kl = F.kl_div(action_logprobs, old_action_probs, reduction='batchmean')
            policy_loss = aux_loss + loss_kl

            # update_network_(policy_loss, self.opt_actor)
            policy_loss.backward()
            self.pi_optimizer.step()

            # paper says it is important to train the value network extra during the auxiliary phase
            self.vf_optimizer.zero_grad()
            # values = self.critic(states)
            values = self.ac.v(obs)
            values = values.flatten()
            value_loss = self._clipped_value_loss(values, rewards, old_values, self.value_clip)
            
            # update_network_(value_loss, self.opt_critic)
            value_loss.backward()
            self.vf_optimizer.step()

        train_maps["end_time - start_time"] += time.time() - self.start_time
        train_maps["train_aux_iter"] = train_aux_iter
        self.start_time = time.time()

        self.aux_buffer = PpgAuxBuffer()
        return train_maps
