import torch
import numpy as np

class RayBuffer():
    def __init__(self):
        self.flag = True
        self.data = {}
        pass
    
    def put(self, sample):
        if self.flag:
            self.flag = False
            self.data = sample
            return
        for k in sample[0].keys():
            self.data[0][k] = np.vstack((self.data[0][k], sample[0][k]))
            print(self.data[0][k].shape)

        for k in sample[1].keys():
            self.data[1][k] = np.hstack((self.data[1][k], sample[1][k]))
            print(self.data[1][k].shape)
        pass

    def get(self):
        data: dict = self.data[0]
        for i in range(1, len(self.data)):
            data.update(self.data[i])
        return {k: torch.as_tensor(v, dtype=torch.float32) for k,v in data.items()}