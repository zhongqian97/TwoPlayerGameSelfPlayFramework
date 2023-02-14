class SelfplayAgent(): # 类似Pipe，对应图中的AgentPipe
    def __init__(self, agent):
        self.agent = agent
        self.action = "reset"
        pass
    
    def send(self, data):
        if data is None:
            return
        
        if isinstance(data, list):
            if data[0] is None:
                return
            self.action = self.agent.infer(data[0], info={"mask": data[1]})[0]
        else:
            self.action = self.agent.infer(data)[0]
        pass
    
    def recv(self):
        if self.action != "reset":
            action = self.action
            self.action = "reset"
            return ["step", action]
        return "reset"