import threading, logging, abc, traceback, time
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
        result = None
        try:
            self.mTask._setLock(pool.getLock())
            result = self.mTask.execIt()
        except Exception:
            rep = StringIO()
            traceback.print_exc(file = rep)
            logging.error("Task failed:" +
                self.mTask.getDescr() + "\n" + rep.getvalue())
            self.mTask.setStatus("Failed, ask tech support")
        self.mTask._setLock(None)
        pool.setResult(self.mTask, result)

#===============================================
class Worker(threading.Thread):
    def __init__(self, master):
        threading.Thread.__init__(self)
        self.mMaster = master
        self.start()

    def run(self):
        while True:
            task_h = self.mMaster._pickTask()
            if task_h is None:
                break
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
        self.mTerminating = False

        self.mWorkers = [Worker(self)
            for idx in range(int(thread_count))]

    def getLock(self):
        return self.mLock

    def close(self):
        with self.mThrCondition:
            self.mTerminating = True
            self.mThrCondition.notify()
        for cnt in range(1000):
            with self.mThrCondition:
                if all([not w.is_alive() for w in self.mWorkers]):
                    return
            time.sleep(.001)

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
                if self.mTerminating:
                    return None
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
