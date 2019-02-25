import threading, logging, abc, traceback
from StringIO import StringIO
from uuid import uuid4

#===============================================
class ExecutionTask:
    def __init__(self, descr):
        self.mUID = uuid4().int
        self.mDescr = descr
        self.mStatus = "Waiting for start..."
        self.mLock = None

    def _setLock(self, lock):
        self.mLock = lock

    def getUID(self):
        return self.mUID

    def getDescr(self):
        return self.mDescr

    def getStatus(self):
        return self.mStatus

    def setStatus(self, status):
        if self.mLock:
            with self.mLock:
                self.mStatus = status
        else:
            self.mStatus = status

    @abc.abstractmethod
    def execIt(self):
        assert False

#===============================================
class TaskHandler:
    def __init__(self, task, ord_no, priority):
        self.mTask     = task
        self.mOrdNo    = ord_no
        self.mPriority = priority

    def getOrd(self):
        return (self.mPriority, self.mOrdNo)

    def execIt(self, pool):
        try:
            self.mTask._setLock(pool.getLock())
            result = self.mTask.execIt()
            pool.setResult(self.mTask, result)
        except Exception:
            rep = StringIO()
            traceback.print_exc(file = rep)
            logging.error("Task failed:" +
                self.mTask.getDescr() + "\n" + rep.getvalue())
            self.mTask.setStatus("Failed, ask tech support")
            pool.setResult(self.mTask, None)
        finally:
            self.mTask._setLock(None)

#===============================================
class Worker(threading.Thread):
    def __init__(self, master):
        threading.Thread.__init__(self)
        self.mMaster = master
        self.start()

    def run(self):
        while True:
            task_h = self.mMaster._pickTask()
            task_h.execIt(self.mMaster)

#===============================================
class JobPool:
    def __init__(self, thread_count, pool_size):
        self.mThrCondition = threading.Condition()
        self.mLock = threading.Lock()

        self.mTaskPool   = []
        self.mPoolSize   = int(pool_size)
        self.mTaskCount  = 0
        self.mActiveTasks = dict()
        self.mResults    = dict()

        self.mWorkers = [Worker(self)
            for idx in range(int(thread_count))]

    @classmethod
    def create(cls, config, prefix, one_thread = False):
        if one_thread:
            thread_count = 1
        else:
            thread_count = config.get(prefix + ".threads-count", as_int = True)
        pool_size = config.get(prefix + ".pool-size", strip_it = True)
        return cls(thread_count, pool_size)

    def getLock(self):
        return self.mLock

    def putTask(self, task, priority = 10):
        with self.mThrCondition:
            if len(self.mTaskPool) >= self.mPoolSize:
                task.setStatus("POOL-OVERFLOW")
                self.setResult(task, None)
            else:
                self.mTaskPool.append(TaskHandler(task,
                    self.mTaskCount, priority))
                self.mTaskCount += 1
                self.mTaskPool.sort(key = TaskHandler.getOrd)
                self.mActiveTasks[task.getUID()] = task
            self.mThrCondition.notify()
        return None


    def setResult(self, task, result):
        with self.mLock:
            if task.getUID() in self.mActiveTasks:
                del self.mActiveTasks[task.getUID()]
            self.mResults[task.getUID()] = [result, task.getStatus()]

    def _pickTask(self):
        while True:
            with self.mThrCondition:
                with self.mLock:
                    if len(self.mTaskPool) > 0:
                        return self.mTaskPool.pop()
                self.mThrCondition.wait()

    def askTaskStatus(self, task_uid):
        with self.mLock:
            if task_uid in self.mResults:
                return self.mResults[task_uid]
            if task_uid in self.mActiveTasks:
                return [False, self.mActiveTasks[task_uid].getStatus()]
