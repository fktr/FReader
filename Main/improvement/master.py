import threading
from queue import Queue

from multiprocessing.managers import BaseManager

from Main.models import Channel

taskq0 = Queue()
taskq1 = Queue()
resultq0 = Queue()
resultq1 = Queue()
BaseManager.register('get_task_queue_0', callable=lambda: taskq0)
BaseManager.register('get_task_queue_1',callable=lambda :taskq1)
BaseManager.register('get_result_queue_0', callable=lambda: resultq0)
BaseManager.register('get_result_queue_1',callable=lambda :resultq1)
manager = BaseManager(address=('', 5000), authkey=b'haha')
manager.start()

class Master:

    def __init__(self):
        self.taskqs=[manager.get_task_queue_0(),manager.get_task_queue_1()]
        self.resultqs=[manager.get_result_queue_0(),manager.get_result_queue_1()]
        self.channels=Channel.objects.all().distinct()
        self.flag=0

    def task_schedule(self):
        for channel in self.channels:
            self.taskqs[self.flag].put(channel)
            print('Put task %s into task queue %d ...' %(channel,self.flag))
            self.flag^=1

    def wait_for_result(self,resultq,index):
        while True:
            try:
                result=resultq.get(timeout=600)
                print('Get result %s from result queue %d ...' %(result[0],index))
                #self.resultq.task_done()
                for item in result:
                    item.save()
            except:
                break

    def wait_for_other_hosts(self):
        for i in range(len(self.resultqs)):
            thread=threading.Thread(target=self.wait_for_result,args=(self.resultqs[i],i))
            thread.start()

'''
    def wait_for_end(self):
        self.resultq.join()
        print('Bingo!')
'''