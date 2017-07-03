from log import debugPrint

'''
This is the definition of a task / experiment, which contained record of all stages
'''
class expTask(object):
    def __init__(self, jid, exp_site_name, exp_arrive_time, exp_setup_elapse, exp_elapse, raw_datasize, \
                 proc_time, nodes, res_datasize):
        super(expTask, self).__init__()
        self.jid              = jid
        self.exp_site_name    = exp_site_name              # name of the science site where this experiment was done
        self.exp_arrive_time  = exp_arrive_time            # time when job arrive at its science site
        self.exp_setup_elapse = exp_setup_elapse           # elapse of time on setting up the experiment 
        self.exp_elapse       = exp_elapse                 # elapse of time on experiment
        self.raw_datasize     = raw_datasize               # size of the experiment data
        self.ready_time       = None                       # time when raw data is ready, for calculating slowdown
        self.proc_time        = proc_time                  # time needed for processing / analyzing the experiment data
        self.req_node         = nodes                      # number of nodes required by this job
        self.res_datasize     = res_datasize               # size of analyzing results
        self.allset           = False                      # True means job was done

        self.resvBW           = None                       # reserved bandwidth
        self.rawTrsProgess    = 0                          # bytes transferred, updated in event
        self.effective_bw     = None
        self.effective_bw_s   = None
        self.rawPath          = None                       # the selected path to transfer raw data
        self.resPath          = None                       # the selected path to transfer result data

        self.hpc_site_name    = None                       # HPC site name for data analysis 
        self.hpc_site         = None                       # HPC site for data analysis 
        self.scheduled_rt     = None                       # scheduled starting run time
        self.allset_ts        = None
        self.exp_setup_event  = None                       # event that will be triggered when setup done
        self.exp_event        = None                       # event for experiment
        self.raw_trs_event    = None                       # event when raw data was transferred, this is the last event 
                                                           # becuase it changes based on link load
        self.run_st_event     = None
        self.run_event        = None                       # event when data analysis is done
        self.res_trs_event    = None                       # event when results transfer is done.


