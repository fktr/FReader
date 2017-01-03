import threading

import time


class PeriodTimer:

    def __init__(self,interval):
        self.interval=interval
        self.flag=0
        self.condlock=threading.Condition()

    def run(self):
        while True:
            time.sleep(self.interval)
            with self.condlock:
                self.flag^=1
                self.condlock.notify_all()

    def wait_for_tick(self):
        with self.condlock:
            last_flag=self.flag
            while last_flag==self.flag:
                self.condlock.wait()

    def start(self):
        t=threading.Thread(target=self.run,daemon=True)
        t.start()
