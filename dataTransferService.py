from log import debugPrint
from simuPara import simuConfig as cfg
from network import networkConfig
import numpy as np
import ns.core
'''
This is a model of data transfer service
'''
class dataTransferService(object):
    """docstring for dataTrs"""
    def __init__(self):
        super(dataTransferService, self).__init__()
        self.linkResv = dict()                   # k=(src-router, dst-router) value = job
        self.gbl_scheduler = None
        self.netcfg = networkConfig()
        self.linkUtilization = dict()

    # Data Transfer and job running are synchronized by bandwidth reservation. i.e., raw data
    # transferring are guaranteed to be done before the scheduled job starting time at HPC site
    def addJob(self, job):
        src, dst = job.exp_site_name, job.hpc_site_name
        # reserve BW
        min_rest_bw_share = float('inf')
        related_jobs = set()
        path = job.rawPath
        for i in range(len(path)-1): 
            s, d = path[i], path[i+1]
            if self.linkResv.get((s, d)) is not None:
                self.linkResv[(s, d)].append(job)
            else:
                self.linkResv[(s, d)] = [job]
            related_jobs.union(set(self.linkResv[(s, d)]))

            # monitoring bytes transfered by each link
            if self.linkUtilization.get((s, d)) is None: self.linkUtilization[(s, d)] = 0
            self.linkUtilization[(s, d)] += job.raw_datasize

            # fair share the rest of the bandwidth (in order to calculate transfer done time)
            min_rest_bw_share = min(min_rest_bw_share, \
                                    (self.netcfg.linkInfo[(s,d)][0] - np.sum([j.resvBW for j in self.linkResv[(s, d)]])) / \
                                    len(self.linkResv[(s, d)])
                                   )
        effctive_bw = job.resvBW + min_rest_bw_share
        debugPrint("<%s, %d> got %.2f extra bandwidth from fair share" % (job.exp_site_name, job.jid, min_rest_bw_share), 0)
        job.effective_bw   = effctive_bw
        job.effective_bw_s = ns.core.Now().GetSeconds()
        # create raw data transfer done event
        job.raw_trs_event = ns.core.Simulator.Schedule(ns.core.Seconds(job.raw_datasize / effctive_bw), self.rawTrsFinishCB, job)
        # update the event of other jobs
        for j in related_jobs:
            self.updateFinshEvent(j)
        # job.hpc_site.

    def updateFinshEvent(self, job):
        ns.core.Simulator.Cancel(job.raw_trs_event)
        job.rawTrsProgess += (ns.core.Now().GetSeconds() - job.effective_bw_s) * job.effective_bw

        src, dst = job.exp_site_name, job.hpc_site_name
        path = job.rawPath
        min_rest_bw_share = float('inf')
        for i in range(len(path)-1): 
            s, d = path[i], path[i+1]
            min_rest_bw_share = min(min_rest_bw_share, \
                                    (self.netcfg.linkInfo[(s,d)][0] - np.sum([j.resvBW for j in self.linkResv[(s, d)]])) / \
                                    len(self.linkResv[(s, d)])
                                   )
        
        effctive_bw = job.resvBW + min_rest_bw_share
        job.effective_bw   = effctive_bw
        job.effective_bw_s = ns.core.Now().GetSeconds()

        job.raw_trs_event = ns.core.Simulator.Schedule(ns.core.Seconds((job.raw_datasize - job.rawTrsProgess) / effctive_bw), \
                                                       self.rawTrsFinishCB, job)

    def getFreeBW(self, src, dst):
        paths = self.netcfg.end2endPath[(src, dst)]
        e2e_free_bw, path_sel = 0, None
        for path in paths:
            path_free_bw = float('inf')
            for i in range(len(path)-1): # get max free bw from src to dst (i.e., min along the path)
                s, d = path[i], path[i+1]
                if self.linkResv.get((s, d)) is not None:
                    path_free_bw = min(path_free_bw, self.netcfg.linkInfo[(s,d)][0] - np.sum([j.resvBW for j in self.linkResv[(s, d)]]))
                else:
                    path_free_bw = min(path_free_bw, self.netcfg.linkInfo[(s,d)][0])
            if path_free_bw > e2e_free_bw:
                e2e_free_bw, path_sel = path_free_bw, path

        return e2e_free_bw * cfg.net_max_resv, path_sel   # will just use a portion of available bandwidth (cfg.net_max_resv), left some for future jobs

    # need update trs event of other related transfers
    def rawTrsFinishCB(self, job):
        src, dst = job.exp_site_name, job.hpc_site_name
        # reserve BW
        path = job.rawPath
        for i in range(len(path)-1): 
            s, d = path[i], path[i+1]
            self.linkResv[(s, d)].remove(job)
        
        job.rawTrsProgess += (ns.core.Now().GetSeconds() - job.effective_bw_s) * job.effective_bw
        # process those jobs which cannot get free bandwidth when it was ready
        self.gbl_scheduler.processSuspendingJobs()
        if job.scheduled_rt - ns.core.Now().GetSeconds() > 5:  # set a threshold just want to save computing time, i.e., not worthwhile to try
            debugPrint("Job <%s, %d> RAW TRS completed %.2f seconds ahead" % (job.exp_site_name, job.jid, \
                        job.scheduled_rt - ns.core.Now().GetSeconds()), level = 0)
            if cfg.rescheduleEAJ: job.hpc_site.rescheduleJob(job)
        # update the raw trs complete event of jobs that share link(s) with this path
        src, dst = job.exp_site_name, job.hpc_site_name
        related_jobs = set()
        path = job.rawPath
        for i in range(len(path)-1): 
            s, d = path[i], path[i+1]
            related_jobs.union(set(self.linkResv[(s, d)]))

        for j in related_jobs:
            self.updateFinshEvent(j)