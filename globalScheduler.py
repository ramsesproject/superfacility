from log import debugPrint
from expTask import expTask
import numpy as np
from simuPara import simuConfig as cfg
import ns.core

class globalScheduler(object):
    def __init__(self):
        super(globalScheduler, self).__init__()
        self.expSites  = list()
        self.compSites = list()
        self.jobTable  = dict()
        self.rawDTS    = None
        self.taskQ     = list()                  # unscheduled task due to zero-bandwidth or no resource

    def recvNewJob(self, job):
        self.jobTable[(job.exp_site_name, job.jid)] = job
        # return   # to be used to generate jobs only
        # iterated over each HPC site for the earliest avaliable time
        target_hpc, sel_path = None, None
        target_rt  = float('inf')
        for hpc in self.compSites:
            free_bw, path =  self.rawDTS.getFreeBW(job.exp_site_name, hpc.name)
            if free_bw < cfg.minBW: continue     # if the available bandwidth is below a threshold, it is better to wait becuase it may suffer
            min_t_dts     = job.raw_datasize / free_bw
            earliest_res_t= hpc.getEarliestRes(job, min_t_dts+ns.core.Now().GetSeconds())
            if target_rt  > earliest_res_t:
                target_rt = earliest_res_t
                target_hpc, sel_path = hpc, path
                
        if target_hpc is None:    # no bandwidth available
            if job not in self.taskQ: self.taskQ.append(job)
            debugPrint("no  bandwidth available @ %f for job <%s, %d> => %d" % (ns.core.Now().GetSeconds(), \
                       job.exp_site_name, job.jid, len(self.taskQ)), level=1)
            return False
        # update this hpc resource reservation to hpc site
        job.hpc_site_name = target_hpc.name
        job.hpc_site      = target_hpc
        job.rawPath       = sel_path
        job.scheduled_rt  = target_rt
        job.resvBW        = job.raw_datasize / (job.scheduled_rt - ns.core.Now().GetSeconds())
        
        debugPrint( "@ %f, experiment <%s, %d> is scheduled to %s to run @ %f" % (ns.core.Now().GetSeconds(), \
              job.exp_site_name, job.jid, job.hpc_site_name, job.scheduled_rt) , level = 0)

        target_hpc.addJob(job)

        # send job to data transfer service
        self.rawDTS.addJob(job)

        return True

    def processSuspendingJobs(self):
        for job in self.taskQ:
            if self.recvNewJob(job): self.taskQ.remove(job)

    def addExpSite(self, site):
        self.expSites.append(site)

    def addCompSite(self, site):
        self.compSites.append(site)



