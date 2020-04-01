#  Copyright (c) 2019. Partners HealthCare and other members of
#  Forome Association
#
#  Developed by Sergey Trifonov based on contributions by Joel Krier,
#  Michael Bouzinier, Shamil Sunyaev and other members of Division of
#  Genetics, Brigham and Women's Hospital
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import threading, abc, time
from uuid import uuid4
from collections import defaultdict

from .log_err import logException
#===============================================
class ExecutionTask:
    def __init__(self, descr):
        self.mUID = uuid4().int
        self.mDescr = descr
        self.mStatus = "Waiting for start..."
        self.mPool = None

    def _reset(self):
        assert self.mPool is None
        self.mStatus = "Waiting for start..."

    def _setPool(self, pool):
        self.mPool = pool

    def getUID(self):
        return self.mUID

    def getDescr(self):
        return self.mDescr

    def getStatus(self):
        return self.mStatus

    def setStatus(self, status):
        if self.mPool:
            with self.mPool.getLock():
                self.mStatus = status
        else:
            self.mStatus = status

    @abc.abstractmethod
    def getTaskType(self):
        assert False

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
            self.mTask._setPool(pool)
            result = self.mTask.execIt()
        except Exception:
            logException("Task failed:" + self.mTask.getDescr())
            self.mTask.setStatus("Failed, ask tech support")
            result = None
        self.mTask._setPool(None)
        pool.setResult(self.mTask, result, self.mOrdNo)

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
class PeriodicalWorker(threading.Thread):
    def __init__(self, master, name, func, timeout):
        threading.Thread.__init__(self)
        self.mMaster = master
        self.mName = name
        self.mFunc = func
        self.mTimeout = timeout
        self.start()

    def run(self):
        while True:
            try:
                self.mFunc()
            except Exception:
                logException("Periodic work %s failed" % self.mName)
            self.mMaster._sleep(self.mTimeout)

#===============================================
class JobPool:
    def __init__(self, thread_count, pool_size, memory_length):
        self.mThrCondition = threading.Condition()
        self.mLock = threading.Lock()

        self.mTaskPool   = []
        self.mPoolSize   = int(pool_size)
        self.mMemLength = memory_length
        self.mTaskCounts  = defaultdict(int)
        self.mActiveTasks = dict()
        self.mResults    = dict()
        self.mTerminating = False

        self.mWorkers = [Worker(self)
            for idx in range(int(thread_count))]
        self.mPeriodicalWorkers = dict()

    def getLock(self):
        return self.mLock

    def addPeriodicalWorker(self, name, func, timeout):
        with self.mThrCondition:
            assert name not in self.mPeriodicalWorkers
            self.mPeriodicalWorkers[name] = PeriodicalWorker(
                self, name, func, timeout)

    def close(self):
        with self.mThrCondition:
            self.mTerminating = True
            self.mThrCondition.notify()
        for _ in range(1000):
            with self.mThrCondition:
                needs_wait = False
                for w in self.mPeriodicalWorkers.values():
                    if w.is_alive():
                        needs_wait = True
                        break
                for w in self.mWorkers:
                    if w.is_alive():
                        needs_wait = True
                        break
                if not needs_wait:
                    return
            time.sleep(.001)

    def putTask(self, task, priority = 10):
        with self.mThrCondition:
            task_ord_no = self.mTaskCounts[task.getTaskType()]
            self.mTaskCounts[task.getTaskType()] += 1
            if len(self.mTaskPool) >= self.mPoolSize:
                task.setStatus("POOL-OVERFLOW")
                self.mTaskCounts[task.getTaskType()] += 1
                self.setResult(task, None, task_ord_no)
            else:
                self.mTaskPool.append(TaskHandler(task, task_ord_no, priority))
                self.mTaskPool.sort(key = TaskHandler.getOrd)
                self.mActiveTasks[task.getUID()] = task
            self.mThrCondition.notify()

    def _cleanUp(self):
        to_remove = []
        for uid, info in self.mResults.items():
            task_type, task_ord_no = info[2]
            if (task_ord_no
                    < self.mTaskCounts[task_type] - self.mMemLength):
                to_remove.append(uid)
        for uid in to_remove:
            del self.mResults[uid]

    def setResult(self, task, result, task_ord_no):
        with self.mLock:
            if task.getUID() in self.mActiveTasks:
                del self.mActiveTasks[task.getUID()]
            if result is not False:
                self.mResults[task.getUID()] = [result, task.getStatus(),
                    (task.getTaskType(), task_ord_no)]
                self._cleanUp()

    def _pickTask(self):
        while True:
            with self.mThrCondition:
                if self.mTerminating:
                    return None
                with self.mLock:
                    if len(self.mTaskPool) > 0:
                        return self.mTaskPool.pop()
                self.mThrCondition.wait()

    def _sleep(self, timeout):
        with self.mThrCondition:
            self.mThrCondition.wait_for(lambda: self.mTerminating, timeout)

    def askTaskStatus(self, task_uid):
        with self.mLock:
            if task_uid in self.mResults:
                return self.mResults[task_uid][:2]
            if task_uid in self.mActiveTasks:
                return [False, self.mActiveTasks[task_uid].getStatus()]
        return None
