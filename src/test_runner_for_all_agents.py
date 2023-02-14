import ray

from Entity.Utils.config import TestConfig
from test_runner import Testing

if __name__ == '__main__':
    ray.init()
    while(True):
        args = TestConfig(all_agent_test_flag=True)
        Testing(args)