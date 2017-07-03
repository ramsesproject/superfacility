from log import debugPrint
import random,math
from expTask import expTask
import numpy as np
import random
from simuPara import simuConfig as cfg

class taskArrival(object):
    def __init__(self, name, hour_of_day_arrival):
        super(taskArrival, self).__init__()
        self.name = name
        if len(hour_of_day_arrival) != 24:
            debugPrint ("please give hourly arrival in one day", level = 1)
        self.hoda = hour_of_day_arrival
        self.hour = -1
        self.minute = 0
        self.taskID = 0
        self.re_sec = list()   # just for easy coding
    def arrival(self, t, tstep):
        t      =  t % (24 * 60 * 60)
        hour   =  int(t / 3600)
        minute = (t % 3600) / 60.
        second = t % 3600
        ret = list()
        if hour != self.hour:
            self.hour = hour
            self.re_sec = np.sort(np.random.randint(0, 3600, self.hoda[hour]))

        for s in self.re_sec[self.re_sec <= second]:
            # ret.append( expTask(np.random.randint(36, 1440), np.random.randint(600, 1800), np.random.randint(50, 180), \
            #             1e9*np.random.randint(2, 60), 1e9*np.random.randint(2, 60), self.taskID, tstep) )
            ret.append( expTask(cfg.nodesVar[self.name], cfg.expTimeVar[self.name], cfg.compTimeVar[self.name], \
                                cfg.rawDataSize[self.name], cfg.resDataSize[self.name], self.taskID, tstep) )
            self.taskID += 1
        self.re_sec = self.re_sec[self.re_sec > second]
        return ret
