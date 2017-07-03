from log import debugPrint
from simuPara import simuConfig as cfg
import numpy as np
import ns.core 

'''
This is a model for experiment data analysis which include the computing resource pool and a model of 
data analysis 
'''
class computingSite(object):
    def __init__(self, nnode, name):
        super(computingSite, self).__init__()
        self.name      = name
        self.nodes     = nnode                        # total number of nodes
        self.task_list = list()                       # a list of task (object), include scheduled and completed tasks
        self.freeNode  = np.array([(0, nnode), (float('inf'), nnode)])         
                                                      # number of free nodes, a sorted list by time and number of free nodes 
                                                      # e.g., [(t1, 10), (t2, 50)] means that there are 10 free nodes from t1 to t2, 
                                                      # there are 50 nodes after t2

    # for a given resource requirement, get the earliest time when resrouce will be avaliable
    def getEarliestRes(self, job, t_from):
        ret_st = t_from
        i = np.searchsorted(self.freeNode[:, 0], t_from) - 1
        while i < self.freeNode.shape[0] - 1:
            if self.freeNode[i, 1] < job.req_node: 
                ret_st = self.freeNode[i+1, 0]
                i +=1; continue
            for j in range(i+1, self.freeNode.shape[0]):
                # if (self.freeNode[j, 1] >= job.req_node) and (self.freeNode[j, 0] - ret_st >= job.proc_time): 
                # be careful with float point comparing
                if (self.freeNode[j, 0] - ret_st >= job.proc_time) or (np.abs(self.freeNode[j, 0] - ret_st - job.proc_time) < 1e-2): 
                    # print self.freeNode, t_from, job.req_node, ret_st
                    return ret_st
                elif self.freeNode[j, 1] < job.req_node: # not enough node avaliable
                    i = j                                      # actually should be j+1, will add after this loop
                    ret_st = self.freeNode[j+1, 0]
                    break  
                elif self.freeNode[j, 0] - ret_st < job.proc_time:
                    continue
                else:
                    debugPrint("something wrong!!!", level = 1)
            i += 1

        debugPrint( "cannot have allocate %d nodes at HPC-%s" % (job.req_node, self.name), level = 1)
        return float('inf')

    def rescheduleJob(self, job):
        # cancel current job reservation
        self.task_list.remove(job)                                                   # remove from the list to avoid duplication
        ns.core.Simulator.Cancel(job.run_st_event)                                   # cancel the scheduled job-starting-event
        run_st, run_end = job.scheduled_rt, job.scheduled_rt + job.proc_time
        idxs = np.searchsorted(self.freeNode[:, 0], run_st,  side='left')            # sure there is an event at run_st and run_end seerately
        idxe = np.searchsorted(self.freeNode[:, 0], run_end, side='left')

        self.freeNode[idxs:idxe, 1] += job.req_node
        if (idxs > 0) and (self.freeNode[idxs, 1] == self.freeNode[idxs-1, 1]):
            self.freeNode = np.delete(self.freeNode, idxs, 0)
            if self.freeNode[idxe-1, 1] == self.freeNode[idxe-2, 1]:
                self.freeNode = np.delete(self.freeNode, idxe-1, 0)

        elif self.freeNode[idxe, 1] == self.freeNode[idxe-1, 1]:
            self.freeNode = np.delete(self.freeNode, idxe, 0)
        # reschedule for the job 
        new_rt = self.getEarliestRes(job, ns.core.Now().GetSeconds())
        if np.abs(job.scheduled_rt - new_rt) > 2:
            debugPrint("Job <%s, %d> will run @ %f, not @ %f!" % (job.exp_site_name, job.jid, \
                    new_rt, job.scheduled_rt), level = 1)
            
        job.scheduled_rt = new_rt
        self.addJob(job)

    # add a job to this computing site
    def addJob(self, job):
        self.task_list.append(job)
        run_st, run_end = job.scheduled_rt, job.scheduled_rt + job.proc_time
        if run_st > self.freeNode[-1, 0] or run_st < self.freeNode[0, 0]: debugPrint("invalid starting time", level = 1)
        idxs = np.searchsorted(self.freeNode[:, 0], run_st,  side='right')
        idxe = np.searchsorted(self.freeNode[:, 0], run_end, side='right')
        for i in range(idxs, idxe): self.freeNode[i, 1] -= job.req_node
        if self.freeNode[idxs-1, 0] == run_st:  self.freeNode[idxs-1, 1] -= job.req_node; 
        if self.freeNode[idxe-1, 0] == run_end: self.freeNode[idxe-1, 1] += job.req_node;    # do not need to subtract

        idxs_v = self.freeNode[idxs-1, 1] - job.req_node
        if self.freeNode[idxs-1, 0] != run_st:  
            self.freeNode = np.insert(self.freeNode, idxs, np.array([run_st,  idxs_v]), axis=0)
            idxe_v = self.freeNode[idxe, 1] + job.req_node
            if self.freeNode[idxe, 0] != run_end: self.freeNode = np.insert(self.freeNode, idxe+1, np.array([run_end, idxe_v]), axis=0)
        else:
            idxe_v = self.freeNode[idxe-1, 1] + job.req_node
            if self.freeNode[idxe-1, 0]!=run_end: self.freeNode = np.insert(self.freeNode, idxe, np.array([run_end, idxe_v]), axis=0)

        job.run_st_event = ns.core.Simulator.Schedule(ns.core.Seconds(job.scheduled_rt-ns.core.Now().GetSeconds()), \
                                                    self.startJobCB, job)
        debugPrint("@ %f, HPC-%s Received a Job from %s with ID %d!" % (ns.core.Now().GetSeconds(), self.name, \
                   job.exp_site_name, job.jid), level = 0) 

    def startJobCB(self, job):
        # job can become ready before its run schedule, it is good to check if there are resource avaliable at this time
        if np.abs(ns.core.Now().GetSeconds() - job.scheduled_rt) < 1:  
            job.run_event = ns.core.Simulator.Schedule(ns.core.Seconds(job.proc_time), self.runFinishCB, job)
        else:
            # should never come here
            debugPrint("Job <%s, %d> ready @ %f, will run @ %f!" % (job.exp_site_name, job.jid, \
                       ns.core.Now().GetSeconds(), job.scheduled_rt), level = 10)
            job.run_st_event = ns.core.Simulator.Schedule(ns.core.Seconds(job.scheduled_rt-ns.core.Now().GetSeconds()), \
                                                       self.startJobCB, job)

    def runFinishCB(self, job):
        debugPrint( "@ %f, Job <%s, %d> done with SD=%f, delayed %.1f seconds!" % (ns.core.Now().GetSeconds(), job.exp_site_name, \
                   job.jid, (ns.core.Now().GetSeconds()-job.ready_time)/job.proc_time, \
                   ns.core.Now().GetSeconds()-job.ready_time-job.proc_time), level = 1)
        job.allset    = True
        job.allset_ts = ns.core.Now().GetSeconds()

    def computatingMdl(self, job):
        return job.proc_time
