import time
import ray

from Entity.Agent.task_rollout_worker import TaskRolloutWorker

@ray.remote(num_cpus=4)
class TaskActorParallel():
    # class TaskActor():
    '''获取Manager队列，执行任务；将结果放入任务中。
    '''
    def __init__(self, args, identifier, queue):
        self.task_rollout_worker = TaskRolloutWorker(args, identifier, queue)
        pass

    def rollout(self):
        self.task_rollout_worker.rollout()
        pass

    def close(self):
        self.task_rollout_worker.close()
        pass

# @ray.remote(num_cpus=1)
# class TaskActorParallel():
#     '''获取Manager队列，执行任务；将结果放入任务中。
#     '''
#     def __init__(self, args, identifier, queue):
#         self.task_actor = TaskActor.remote(args, identifier, queue)
#         self.args = args
#         self.identifier = identifier
#         self.queue = queue
#         pass

#     def rollout(self):
#         while True:
#             try:
#                 if self.task_actor is None:
#                     self.task_actor = TaskActor.remote(self.args, self.identifier, self.queue)
#                 id = self.task_actor.rollout.remote()
#                 ray.get(id, timeout=int(self.args["worker_timeout"]))
#             except Exception:
#                 print('An exception occurred')
#                 time.sleep(int(self.args["worker_timeout"]))
            


#     def close(self):
#         self.task_actor.close.remote()
#         pass