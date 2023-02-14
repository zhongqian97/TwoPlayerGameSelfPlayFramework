import time
from ray.util.queue import Queue
import numpy as np
import ray

class TaskManager():
    """任务管理器
    工作职责：
    将任务内容放入队列中，填充整个队列
    检测任务状态，旧任务销毁，迭代新任务
    """
    def __init__(self, args) -> None:
        self.parallel_task_list = []
        self.need_to_fill = args["env_num"]
        self.max_size = args["env_num"] * 2
        self.queue = Queue(maxsize=self.max_size)
        self.not_change_flag = 0
        pass

    def add_parallel_task(self, task):
        """添加平行任务
        """
        self.parallel_task_list.append(task)

    def processing(self):
        """整个处理的过程，处理完成后返回True
        1、检测任务状态
        2、将任务内容放入队列中，填充整个队列（填充量为当前的环境总数）
        """
        self.has_reset_actors = False
        while len(self.parallel_task_list) > 0:
            for i in range(len(self.parallel_task_list)):
                if self.parallel_task_list[i] == None:
                    self.has_reset_actors = True
                    del self.parallel_task_list[i]
            can_use_task_list = self.check_task_status()
            if len(can_use_task_list) > 0:
                can_use_task_list_p = self.multi_task_scheduling_algorithm(can_use_task_list)
                self.queue_create(can_use_task_list, can_use_task_list_p)
            time.sleep(1)
        return True, self.has_reset_actors

    def check_task_status(self):
        """检测任务状态并返回可用任务
        """
        can_use_task_list = []
        can_use_task_id_list = [
            task.processing_and_get_status.remote() for task in self.parallel_task_list 
        ]

        for i in range(len(can_use_task_id_list)):
            status = ray.get(can_use_task_id_list[i])
            
            if status == "handling_and_create":
                can_use_task_list.append(self.parallel_task_list[i])

            if status == "end":
                self.parallel_task_list[i].processing.remote()
                next_task = ray.get(self.parallel_task_list[i].next.remote())
                self.parallel_task_list[i] = next_task
                self.has_reset_actors = True

        for i in range(len(self.parallel_task_list)):
            if self.parallel_task_list[i] == None:
                del self.parallel_task_list[i]
                self.has_reset_actors = True

        return can_use_task_list

    def queue_create(self, can_use_task_list, can_use_task_list_p):
        """队列内容生成
        """
        q_size = self.queue.size()
        print("q_size: " + str(q_size))
        if self.not_change_flag == len(can_use_task_list) and q_size >= self.need_to_fill:
            return
        self.not_change_flag = len(can_use_task_list) # 检测是否队列发生变化，变化立刻清空队列，防止有旧内容（加速）。
        stored_size = self.max_size - q_size
        try:
            self.queue.get_nowait_batch(q_size)
        
            for _ in range(self.max_size):
                i = np.random.choice(len(can_use_task_list), p=can_use_task_list_p)
                self.queue.put(can_use_task_list[i].create.remote(), block=False)
        except Exception:
            pass
        pass

    def multi_task_scheduling_algorithm(self, can_use_task_list):
        """多任务之间的调度算法
        """
        can_use_task_list_p = []
        for _ in range(len(can_use_task_list)):
            can_use_task_list_p.append(1 / len(can_use_task_list))
        return can_use_task_list_p
    
