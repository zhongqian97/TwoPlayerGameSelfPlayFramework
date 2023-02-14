from Entity.Agent.rl_agent_factory import CreateAgent
import ray
class TrainModel():
    def __init__(self, samples, step) -> None:
        self.samples = samples
        self.step = step
        pass

@ray.remote(num_cpus=1)
class PPOAgentRay():
    def __init__(self, args=None, env=None):
        self.agent = CreateAgent(args=args, env=env)
        pass
    
    def load(self, ai_name, model=None):
        return self.agent.load(ai_name, model=model)
    
    def save(self, epoch):
        self.agent.save(epoch)
        pass
    
    def get_weights(self):
        return self.agent.get_weights()
    
    def train(self, train_model: TrainModel):
        return self.agent.train(train_model.samples, train_model.step)
    
    def get_train_maps_list(self):
        return self.agent.train_maps_list
    
    def close(self):
        self.agent.close()
        pass

class Trainer():
    def __init__(self, args=None, env=None):
        self.agent = PPOAgentRay.remote(args=args, env=env)
        pass
    
    def load(self, ai_name, model=None):
        return ray.get(self.agent.load.remote(ai_name, model=model))
    
    def save(self, epoch):
        ray.get(self.agent.save.remote(epoch))
        pass
    
    def get_weights(self):
        return ray.get(self.agent.get_weights.remote())
    
    def train(self, samples, step):
        train_model = TrainModel(samples, step)
        train_model_id = ray.put(train_model)
        return ray.get(self.agent.train.remote(train_model_id))
    
    def close(self):
        ray.get(self.agent.close.remote())
        pass
    
    def get_train_maps_list(self):
        return ray.get(self.agent.get_train_maps_list.remote())