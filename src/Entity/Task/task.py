from abc import ABCMeta,abstractmethod  

class ATask():
    """抽象的Task类（接口），用于生成并处理任务。
    接口的调用流程：
    preHandle 用于进行任务的预处理 > 处理对象为任务本身。
        |
        V
        while
            while 
                create 用于任务队列生成并交给执行器运行 > 处理对象为任务管理器。
                    |
                    V
                handling 用于进行执行器任务完成的最终验证 > 处理对象为任务本身。
            |
            V
        postHandle 用于进行任务的后处理 > 处理对象为任务本身。
        |
        V
    next 用于生成新的任务 > 处理对象为任务管理器。

    任务接口的状态周期：
    preHandle（任务前处理）
     -> handling_and_create / handling_no_create（任务处理中，在该阶段中任务管理器可以放入内容 / no_create 子状态时无法创建内容）
     -> postHandle（任务后处理，并判断是否进入任务终止还是继续进行处理）
     -> end 任务终止（该阶段任务管理器销毁任务并在任务链中获取下一个任务）。
    """
    __metaclass__ = ABCMeta #指定这是一个抽象类  
    
    @abstractmethod  #抽象方法  
    def preHandle(self):
        pass

    @abstractmethod
    def create(self):
        pass
    
    @abstractmethod
    def handling(self):
        pass

    @abstractmethod
    def postHandle(self):
        pass
    
    @abstractmethod
    def next(self):
        pass
    