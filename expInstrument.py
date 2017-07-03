from log import debugPrint
from expTask import expTask
import numpy as np
from simuPara import simuConfig as cfg
import ns.core 

'''
This is a model for beamline / experiment instrument
'''
class expInstrument(object):
    def __init__(self, name, ds_range, tsetup, tcollect, global_scheduler, jid_generator, tech="XPCS"):
        super(expInstrument, self).__init__()
        self.name         = name                 # name of the facility, work as an identity
        self.tsetup       = tsetup               # experiment setup time [min, max]
        self.tcollect     = tcollect             # experiment time [min, max]
        self.ds_range     = ds_range             # dataset size range [min, max]
        self.global_scheduler = global_scheduler
        self.jid_generator= jid_generator
        self.schedule_i   = 0
        self.technique    = tech
        
    def expSetupFinishCB(self, job):
        debugPrint( "experiment <%s, %d> setup done @ %f, elapsed %s" % (job.exp_site_name, \
              job.jid, ns.core.Now().GetSeconds(), job.exp_setup_elapse), level = 0 )
        job.exp_event   = ns.core.Simulator.Schedule(ns.core.Seconds(job.exp_elapse),   self.expFinishCB, job)

    def expFinishCB(self, job):
        debugPrint( "experiment <%s, %d> is ready to analysis @ %f, exp elapsed %s" % (job.exp_site_name, \
               job.jid, ns.core.Now().GetSeconds(), job.exp_elapse), level = 0 )
        job.ready_time = ns.core.Now().GetSeconds()
        self.global_scheduler.recvNewJob(job)
        if ns.core.Now().GetHours() >= np.sum(cfg.expSiteSchedule[self.name][:(self.schedule_i+1)]) and \
           ns.core.Now().GetSeconds() < cfg.simTime:
            self.schedule_i += 1  # skip operating period
            ns.core.Simulator.Schedule(ns.core.Seconds(cfg.expSiteSchedule[self.name][self.schedule_i]*3600), self.initiateJob)
            self.schedule_i += 1  # skip shutdown period
        elif ns.core.Now().GetSeconds() < cfg.simTime:
            self.initiateJob()
        else:
            debugPrint("@ %f entering grace period" % ns.core.Now().GetSeconds(), 0)

    def computing_req(self, tech, ds, proc_time):
        if tech == "Ptychography":
            gflops_per_node = 50.
            nodes     = np.ceil(ds * 1e-3 * 0.51 * 1e6 / (gflops_per_node * proc_time)).astype('int')  # 0.51 PFLO / GB
        else: 
            # nodes     = np.random.randint(4, 256)
            nodes     = max(1, int(np.random.normal(130, 40)) )
        return nodes

    def initiateJob(self):
        jtsetup   = np.random.rand() * (self.tsetup[1]   - self.tsetup[0])   + self.tsetup[0]
        jtcol     = np.random.rand() * (self.tcollect[1] - self.tcollect[0]) + self.tcollect[0]
        raw_datasize = cfg.ds_ratio * (np.random.rand() * (self.ds_range[1] - self.ds_range[0]) + self.ds_range[0])
        res_datasize = 3.5e5
        proc_time = 15 + np.random.rand() * 3600
        nodes     = self.computing_req(None, raw_datasize, proc_time)
        job = expTask(self.jid_generator(), self.name, ns.core.Now().GetSeconds(), \
                      jtsetup, jtcol, raw_datasize, proc_time, nodes, res_datasize)

        debugPrint( "job <%s, %d> arrives @ %f" % (job.exp_site_name, job.jid, ns.core.Now().GetSeconds()), level = 0 )
        job.setup_event = ns.core.Simulator.Schedule(ns.core.Seconds(jtsetup), self.expSetupFinishCB, job)

    def startRunExp(self):
        if cfg.realSchedule:
            if cfg.expSiteSchedule[self.name][0] > 0: 
                ns.core.Simulator.Schedule(ns.core.Seconds(cfg.expSiteSchedule[self.name][0]*3600), self.initiateJob)
            else: 
                ns.core.Simulator.Schedule(ns.core.Seconds(0.1), self.initiateJob)
            self.schedule_i = 1
        else:
            self.initiateJob()


