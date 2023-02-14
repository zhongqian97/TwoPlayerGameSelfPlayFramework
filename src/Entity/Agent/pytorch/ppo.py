import numpy as np
import torch
from torch.optim import Adam
import time
import Entity.Agent.pytorch.core as core
from Entity.Agent.pytorch.ppo_buffer import PPOBuffer


class PPOAgent():
    def __init__(self, args=None, env=None):
        """
        Proximal Policy Optimization (by clipping), 

        with early stopping based on approximate KL

        Args:
            env_fn : A function which creates a copy of the environment.
                The environment must satisfy the OpenAI Gym API.

            actor_critic: The constructor method for a PyTorch Module with a 
                ``step`` method, an ``act`` method, a ``pi`` module, and a ``v`` 
                module. The ``step`` method should accept a batch of observations 
                and return:

                ===========  ================  ======================================
                Symbol       Shape             Description
                ===========  ================  ======================================
                ``a``        (batch, act_dim)  | Numpy array of actions for each 
                                            | observation.
                ``v``        (batch,)          | Numpy array of value estimates
                                            | for the provided observations.
                ``logp_a``   (batch,)          | Numpy array of log probs for the
                                            | actions in ``a``.
                ===========  ================  ======================================

                The ``act`` method behaves the same as ``step`` but only returns ``a``.

                The ``pi`` module's forward call should accept a batch of 
                observations and optionally a batch of actions, and return:

                ===========  ================  ======================================
                Symbol       Shape             Description
                ===========  ================  ======================================
                ``pi``       N/A               | Torch Distribution object, containing
                                            | a batch of distributions describing
                                            | the policy for the provided observations.
                ``logp_a``   (batch,)          | Optional (only returned if batch of
                                            | actions is given). Tensor containing 
                                            | the log probability, according to 
                                            | the policy, of the provided actions.
                                            | If actions not given, will contain
                                            | ``None``.
                ===========  ================  ======================================

                The ``v`` module's forward call should accept a batch of observations
                and return:

                ===========  ================  ======================================
                Symbol       Shape             Description
                ===========  ================  ======================================
                ``v``        (batch,)          | Tensor containing the value estimates
                                            | for the provided observations. (Critical: 
                                            | make sure to flatten this!)
                ===========  ================  ======================================


            ac_kwargs (dict): Any kwargs appropriate for the ActorCritic object 
                you provided to PPO.

            seed (int): Seed for random number generators.

            steps_per_epoch (int): Number of steps of interaction (state-action pairs) 
                for the agent and the environment in each epoch.

            epochs (int): Number of epochs of interaction (equivalent to
                number of policy updates) to perform.

            gamma (float): Discount factor. (Always between 0 and 1.)

            clip_ratio (float): Hyperparameter for clipping in the policy objective.
                Roughly: how far can the new policy go from the old policy while 
                still profiting (improving the objective function)? The new policy 
                can still go farther than the clip_ratio says, but it doesn't help
                on the objective anymore. (Usually small, 0.1 to 0.3.) Typically
                denoted by :math:`\epsilon`. 

            pi_lr (float): Learning rate for policy optimizer.

            vf_lr (float): Learning rate for value function optimizer.

            train_pi_iters (int): Maximum number of gradient descent steps to take 
                on policy loss per epoch. (Early stopping may cause optimizer
                to take fewer than this.)

            train_v_iters (int): Number of gradient descent steps to take on 
                value function per epoch.

            lam (float): Lambda for GAE-Lambda. (Always between 0 and 1,
                close to 1.)

            max_ep_len (int): Maximum length of trajectory / episode / rollout.

            target_kl (float): Roughly what KL divergence we think is appropriate
                between new and old policies after an update. This will get used 
                for early stopping. (Usually small, 0.01 or 0.05.)

            logger_kwargs (dict): Keyword args for EpochLogger.

            save_freq (int): How often (in terms of gap between epochs) to save
                the current policy and value function.

        """
        
        self.train_maps_list = ["step", "kl", "ent", "train_pi_iter", "pi_l_old", "v_l_old", "pi_l_new", "v_l_new",
            "cf", "pi_l_new - pi_l_old", "v_l_new - v_l_old", "end_time - start_time"]
        
        self.train_pi_iters = args["train_pi_iters"]
        self.train_v_iters = args["train_v_iters"]
        self.target_kl = args["target_kl"]
        self.save_freq = args["save_freq"]
        self.clip_ratio = args["clip_ratio"]
        
        actor_critic=core.MLPActorCritic
        lam = args["lam"]
        local_steps_per_epoch = args["local_steps_per_epoch"]
        steps_per_epoch = args["steps_per_epoch"]
        gamma = args["gamma"]
        self.pi_lr = args["pi_lr"]
        self.vf_lr = args["vf_lr"]
        seed = args["seed"]
        self.args = args
        self.entropy = args["entropy"]

        # Random seed
        # seed += 10000
        torch.manual_seed(seed)
        np.random.seed(seed)

        # Instantiate environment
        obs_dim = env.observation_space.shape
        act_dim = env.action_space.shape
        mask_dim = env.mask_space.shape

        self.ac_kwargs=dict(actor_hidden_sizes=[args["actor_hidden_dim"]] * args["ac_networks_layer"],
                        critic_hidden_sizes=[args["critic_hidden_dim"]] * args["ac_networks_layer"],
                        )
        
        # Create actor-critic module
        self.ac = actor_critic(env.observation_space, env.action_space, **self.ac_kwargs)

        # Set up experience buffer
        self.buf = PPOBuffer(obs_dim, act_dim, local_steps_per_epoch, gamma, lam, info={"mask_dim": mask_dim})
        self.train_buf = PPOBuffer(obs_dim, act_dim, steps_per_epoch, gamma, lam, info={"mask_dim": mask_dim})

        # Set up optimizers for policy and value function
        self.pi_optimizer = Adam(self.ac.pi.parameters(), lr=self.pi_lr)
        self.vf_optimizer = Adam(self.ac.v.parameters(), lr=self.vf_lr)

        # Prepare for interaction with environment
        self.start_time = time.time()
        
    
    def max_model_id(self, file_dir):
        import re, os
        all_files = []
        for root, dirs, files in os.walk(file_dir):
            all_files = files

        ids = []
        for filename in all_files:
            try:
                a = re.search('model\d*', filename).span()
            except Exception:
                continue
            ids.append(int(filename[5 + a[0]: a[1]]))
        max_num = max(ids)
        return self._file_name(max_num), max_num

    def _file_name(self, num):
        return 'model{}.pt'.format(num)

    def load(self, ai_name, file_path=None, model=None):
        self.m_nStartEpoch = 1
        import os.path as osp
        if file_path == None:
            self.checkpoints_dir = self.args["file_path"] + ai_name + '/'
        else:
            self.checkpoints_dir = file_path + ai_name + '/'
        try:
            if model == None:
                file_name, m_nStartEpoch = self.max_model_id(self.checkpoints_dir)
            else:
                file_name = self._file_name(model)
                m_nStartEpoch = model
                
            actor_critic = torch.load(self.checkpoints_dir + file_name)
            self.ac = actor_critic
            self.m_nStartEpoch = m_nStartEpoch
            
            self.pi_optimizer = Adam(self.ac.pi.parameters(), lr=self.pi_lr)
            self.vf_optimizer = Adam(self.ac.v.parameters(), lr=self.vf_lr)
            print("load success.")
        except Exception as e:
            print("load model failed", e)
            self.m_nStartEpoch = 1
        return self.m_nStartEpoch

    def close(self):
        pass
    
    def get_weights(self):
        return self.ac
    
    def set_weights(self, model):
        self.ac = model
        pass 
    
    def save(self, epoch):
        import os.path as osp
        if epoch % self.save_freq == 0:
            torch.save(self.ac, self.checkpoints_dir + "model" + str(epoch) + ".pt")
        pass
    
    def infer(self, o, info={}):
        a, _, _ = self.inferAndCollectSample(o, info=info)
        return a

    def inferV(self, o):
        _, v, _ = self.ac.step(torch.as_tensor(o.reshape(1, -1), dtype=torch.float32), flag=False)
        return v
    
    def inferAndCollectSample(self, o, info={}):
        return self.ac.step(torch.as_tensor(o.reshape(1, -1), dtype=torch.float32), 
                        mask=torch.as_tensor(info["mask"], dtype=torch.int8))
    
    # Set up function for computing PPO policy loss
    def _compute_loss_pi(self, data):
        obs, act, adv, logp_old, mask = data['obs'], data['act'], data['adv'], data['logp'], data['mask']

        # Policy loss
        pi, logp = self.ac.pi(obs, mask=mask, act=act)
        ratio = torch.exp(logp - logp_old)

        # ent = pi.entropy().mean().item()
        ent = (-logp).mean().item()

        clip_adv = torch.clamp(ratio, 1-self.clip_ratio, 1+self.clip_ratio) * adv
        loss_pi = -(torch.min(ratio * adv, clip_adv)).mean() - ent * self.entropy

        # Useful extra info
        approx_kl = (logp_old - logp).mean().item()

        clipped = ratio.gt(1+self.clip_ratio) | ratio.lt(1-self.clip_ratio)
        clipfrac = torch.as_tensor(clipped, dtype=torch.float32).mean().item()
        pi_info = dict(kl=approx_kl, ent=ent, cf=clipfrac)

        return loss_pi, pi_info

    # Set up function for computing value loss
    def _compute_loss_v(self, data):
        obs, ret = data['obs'], data['ret']
        return ((self.ac.v(obs) - ret)**2).mean()
            
    def train(self, samples, step):
        data = samples

        pi_l_old, pi_info_old = self._compute_loss_pi(data)
        pi_l_old = pi_l_old.item()
        v_l_old = self._compute_loss_v(data).item()

        # Train policy with multiple steps of gradient descent
        train_pi_iter = self.train_pi_iters
        for i in range(self.train_pi_iters):
            self.pi_optimizer.zero_grad()
            loss_pi, pi_info = self._compute_loss_pi(data)
            kl = np.average(pi_info['kl'])
            if kl > 1.5 * self.target_kl:
                train_pi_iter = i
                break
            loss_pi.backward()
            # mpi_avg_grads(self.ac.pi)    # average grads across MPI processes
            self.pi_optimizer.step()

        # Value function learning
        for i in range(self.train_v_iters):
            self.vf_optimizer.zero_grad()
            loss_v = self._compute_loss_v(data)
            loss_v.backward()
            # mpi_avg_grads(self.ac.v)    # average grads across MPI processes
            self.vf_optimizer.step()

        kl, ent, cf = pi_info['kl'], pi_info_old['ent'], pi_info['cf']
        pi_l_new = loss_pi.item()
        v_l_new = loss_v.item()
        train_maps = {}
        train_maps["step"] = step
        train_maps["train_pi_iter"] = train_pi_iter
        train_maps["kl"] = kl
        train_maps["ent"] = ent
        train_maps["pi_l_old"] = pi_l_old
        train_maps["v_l_old"] = v_l_old
        train_maps["pi_l_new"] = pi_l_new
        train_maps["v_l_new"] = v_l_new
        train_maps["cf"] = cf
        train_maps["pi_l_new - pi_l_old"] = pi_l_new - pi_l_old
        train_maps["v_l_new - v_l_old"] = v_l_new - v_l_old
        train_maps["end_time - start_time"] = time.time() - self.start_time
        
        self.start_time = time.time()

        # assert None != None
        return train_maps