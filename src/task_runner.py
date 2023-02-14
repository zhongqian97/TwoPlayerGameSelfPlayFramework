from venv import create
from Entity.Task.task_actor import TaskActorParallel
from Entity.Task.task_manager import TaskManager
from Entity.Task.test_task import TestTask
from Entity.Task.train_task import TrainTask
from Entity.Utils.bark_log import bark_log
from Entity.Utils.config import FrameConfig

import ray

ray.init(address="auto", _redis_password='5241590000000000')
# ray.init()

def Running(args):
    # 创建任务管理器
    task_manager = TaskManager(args)

    def create_task(fastmode=True):
        # 生成任务
        train_task = TrainTask.remote(args, fastmode=fastmode)
        test_task = TestTask.remote(args)
        set_self_and_next_id = train_task.set_self_and_next.remote(train_task, test_task)
        task_manager.add_parallel_task(train_task)

        # 生成任务
        if args["task_list_loop"] == "True":
            test_task.set_self_and_next.remote(test_task, train_task)
        else:
            test_task.set_self_and_next.remote(test_task, None)
        return set_self_and_next_id

    set_self_and_next_id_list = []
    set_self_and_next_id_list.append(create_task())
    
    if args["fastmode"] == "False":
        set_self_and_next_id_list.append(create_task(fastmode=False))
    # 创建执行器
    task_actor_list = []
    task_actor_list = [TaskActorParallel.remote(args, _, task_manager.queue) for _ in range(args["env_num"])]
    task_actor_ids = []
    def create_or_reset_task_actors(task_actor_ids):
        if len(task_actor_ids) != 0:
            try:
                bark_log("create_or_reset_task_actors")
                ray.cancel(task_actor_ids, force=True, recursive=True)
            except:
                print('An exception occurred in ray.cancel!')
        task_actor_ids = [task_actor.rollout.remote() for task_actor in task_actor_list]
        return task_actor_ids
        
    # 开启执行器
    task_actor_ids = create_or_reset_task_actors(task_actor_ids)
    # 开启任务
    ray.get(set_self_and_next_id_list)

    while True:
        # 任务调度
        has_break, has_reset_actors = task_manager.processing()
        if has_reset_actors:
            task_actor_ids = create_or_reset_task_actors(task_actor_ids)

        if has_break:
            # 任务执行完毕，返回
            break
    pass

if __name__ == '__main__':
    args = FrameConfig()
    import json
    print(json.dumps(args))
    Running(args)