import numpy as np
from dataTransferService import dataTransferService
from experimentSite import experimentSite
from computingSite import computingSite
from expTask import expTask
from simuPara import simuConfig as cfg
from log import debugPrint
import pandas as pd
from globalScheduler import globalScheduler
import ns.core 
import shelve

def envInit():
    expSites    = dict()                         # a global view of all Beamlines
    compSites   = dict()

    rawDTS = dataTransferService()               # data transfer service
    gbl_scheduler = globalScheduler()            # global scheduler
    gbl_scheduler.rawDTS = rawDTS
    rawDTS.gbl_scheduler = gbl_scheduler

    for i in range(len(cfg.expSiteName)):        # experiment sites
        site = experimentSite(cfg.expSiteName[i], gbl_scheduler)
        site.initInstrument()
        site.startInstruments()
        gbl_scheduler.expSites.append(site)
        expSites[site.name] = site

    for i in range(len(cfg.compSiteName)):       # HPC site
        site = computingSite(cfg.compSiteNodes[cfg.compSiteName[i]], cfg.compSiteName[i])
        gbl_scheduler.compSites.append(site)
        compSites[site.name] = site

    return gbl_scheduler, expSites, compSites

# only write job arrival information
def write_job_arrival(gbl_sched, compSites):
    fp = open("job-arrival-%d.csv" % np.sum(cfg.compSiteNodes.values()), "w")
    tlog_header = 'TSid,src,dst,nnode,rawDS,EXPBegin,EXPEnd,runTime\n'
    fp.write(tlog_header)
    for job in gbl_sched.jobTable.values():
        jlog = (job.jid, job.exp_site_name, job.hpc_site_name, job.req_node, job.raw_datasize, job.exp_arrive_time+job.exp_setup_elapse,\
                    job.exp_arrive_time+job.exp_setup_elapse+job.exp_elapse, job.proc_time)
        fp.write(",".join([str(x) for x in jlog]) + "\n")
    fp.close()

# write every detail of each job for statistical analysis
def write_log(gbl_sched, compSites):
    comp_jobs = 0
    fn = "task-log-%d,%.2fnet,%.2fava,%s,ANL-%d,NERSC-%d,ORNL-%d.csv" % (np.sum(cfg.compSiteNodes.values()), cfg.net_ratio, cfg.net_max_resv, \
                                                                         cfg.rescheduleEAJ, cfg.compSiteNodes["ANL"], cfg.compSiteNodes['NERSC'], \
                                                                         cfg.compSiteNodes['ORNL'])

    fp = open(fn, "w")
    tlog_header = 'TSid,src,dst,nnode,rawDS,EXPBegin,EXPEnd,ComPBegin,ComPEnd,SlowDown\n'
    fp.write(tlog_header)
    for job in gbl_sched.jobTable.values():
        if not job.allset: continue
        # sd = (job.allset_ts - job.ready_time) / job.proc_time
        sd = (job.allset_ts - job.ready_time ) / (job.proc_time + job.raw_datasize / (cfg.net_ratio * 100 * 1e3 / 8) )
        jlog = (job.jid, job.exp_site_name, job.hpc_site_name, job.req_node, job.raw_datasize, job.exp_arrive_time+job.exp_setup_elapse,\
                    job.exp_arrive_time+job.exp_setup_elapse+job.exp_elapse, job.scheduled_rt, job.scheduled_rt+job.proc_time, sd)
        fp.write(",".join([str(x) for x in jlog]) + "\n")
        comp_jobs += 1
    fp.close()

    ## write computing resource log
    # header = "timeStamp,Nodes\n"
    # for h in cfg.compSiteName:
    #     fp = open("hpc-log-%s-%d.csv" % (h, np.sum(cfg.compSiteNodes.values())), "w")
    #     fp.write(header)
    #     fp.write("\n".join(["%f, %d" % (x[0], x[1]) for x in compSites[h].freeNode]) )
    #     fp.close()

    return comp_jobs, fn[:-4]

def progress_report(gbl_sched):
    _cnt = 0
    for job in gbl_sched.jobTable.values():
        if job.allset: _cnt += 1
    debugPrint("@ %.1f, %d out of %d jobs are done, progress: %.1f percent" % (ns.core.Now().GetHours(), _cnt, len(gbl_sched.jobTable),\
               100. * ns.core.Now().GetSeconds() / cfg.simTime), 10)
    ns.core.Simulator.Schedule(ns.core.Seconds(cfg.simTime / 20.), progress_report, gbl_scheduler)

def save_session(fn):
    _session = shelve.open(fn,'n') # 'n' for new
    for key in dir():
        try:
            print key
            _session[key] = globals()[key]
        except TypeError:
            print('ERROR shelving: {0}'.format(key))
    _session.close()

def restore_session(fn):
    _session = shelve.open(fn) 
    for key in _session:
        globals()[key] = _session[key]
    _session.close()

if __name__ == '__main__':
    ns.core.Time.SetResolution(ns.core.Time.S)
    np.random.seed(cfg.rndSeed)
    gbl_scheduler, expSites, compSites = envInit()

    ns.core.Simulator.Schedule(ns.core.Seconds(cfg.simTime / 20.), progress_report, gbl_scheduler)

    ns.core.Simulator.Stop(ns.core.Seconds(cfg.simTime + cfg.gracePeriod))
    ns.core.Simulator.Run()
    ns.core.Simulator.Destroy()
    
    comp_jobs, ofn = write_log(gbl_scheduler, compSites)
    # save_session(ofn)
    # write_job_arrival(gbl_scheduler, compSites)
    debugPrint("%d jobs out of %d jods done in %.2f hours!" % (comp_jobs, len(gbl_scheduler.jobTable), cfg.simTime/3600.), level = 10)
    debugPrint("%d jobs suspended due to network !" % (len(gbl_scheduler.taskQ)), level = 10)

    np.save("linkUtilization", gbl_scheduler.rawDTS.linkUtilization)
