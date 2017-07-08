# Introduction

A simulator of super facility for evaluating design choice, decision supporting and unforeseen scenario evaluation. 

# tutorial

## Requiremnt 

* Python 2.7 with numpy and ns3 (https://www.nsnam.org, need to download the code and compile, then install its python binding)

## Module description 

| File               | Module           | Description  |
|:-------------------|:-------------|:-----|
|superFacilitySimu.py| main          | the main entrance |
|expTask.py |expTask| experiment task data structure|
|expInstrument.py | expInstrument |the experiment instrument (data acquisition equipment) model|
|experimentSite.py | experimentSite | experiment facility model |
| globalScheduler.py | globalScheduler | the global job scheduler|
| dataTransferService.py | dataTransferService | data transfer model, also response bandwidth resource management (reserve / release bandwidth) |
| network.py | networkConfig| configuration of network, include topology and bandwidth, RTT feautes has not been use in current version |
| computingSite.py | computingSite | model HPC site, include resource management module|
| simuPara.py | simuConfig | model configuration module, all parameters beside network are saved in this file. users could creat their own scenario via this file |
| log.py | ~ | debug enable / disable/ filter |

## Simulation log

Users need retrieve simulation results from the simulation log. There are two types of log, job logs and resource monitoring log.

### Job logs
This log save the history of each job, the file name contains some key simulation parameter. An example of the file name: task-log-3096,0.20net,1.00ava,False,ANL-1231,NERSC-618,ORNL-1247.csv

TSid | src | dst | nnode | rawDS | EXPBegin | EXPEnd | ComPBegin | ComPEnd | SlowDown
|:----|:---|:-----|:-----|:-----|:-----|:-----|:-----|:-----|:-----|
42490 | APS | NERSC | 95 | 8692.81948852 | 11540591.2328 | 11540790.85 | 11540793.4771 | 11541823.7444 | 0.999279852261
13618 | LCLS | ANL | 103 | 808196.865478 | 9247185.28009 | 9248085.28009 | 9251073.27875 | 9254397.12011 | 1.73040640474
11310 | APS | ORNL | 190 | 10879.8951234 | 2056637.87074 | 2056937.87074 | 2056941.35196 | 2057910.99624 | 0.998977161699
44062 | LCLS | ANL | 160 | 887457.101294 | 24938381.2546 | 24939281.2546 | 24941872.9828 | 24945224.4525 | 1.60315017979
35208 | ALS | ORNL | 100 | 22660.301 | 28199856.0 | 28200368.0 | 28200377.0641 | 28201212.7006 | 0.999170597562
112450 | APS | NERSC | 193 | 19046.5239261 | 31495295.0375 | 31495515.1436 | 31495522.6186 | 31496391.9191 | 0.998951933628
212 | ALS | NERSC | 180 | 3769.96 | 164000.0 | 164100.0 | 164106.507984 | 164982.392758 | 1.0041113198
25630 | NSLS | NERSC | 90 | 9694.9154439 | 25361935.4636 | 25362087.5409 | 25362090.878 | 25364825.9716 | 0.999645273366
81526 | APS | ANL | 142 | 12450.7813732 | 22581605.5518 | 22582170.7197 | 22582174.9803 | 22585254.2688 | 0.999588630413

Where, 

* ___TSid___ is the job id (it is an unique number for jobs from the same site); 

* ___src___ is the name of experiment site;

* ___dst___ is the name of HPC site; 

* ___nnode___ is the number of computing node needed for the job; 

* ___rawDS___ is the size of raw dataset in MByte; 

* ___EXPBegin___ is the time when starting to collect data (right after setup); 

* ___EXPEnd___ is when time collection finished (job ready to be assigned for data analysis); 

* ___ComPBegin___ is the actual time when job start to run; SlowDown is the job slowdown 

### HPC utilization logs
This file save the utilization of HPC resource by events. It has two column (timeStamp,Nodes). Each line represent number of node availabe from current ___timeStamp___ to the ___timeStamp___ of next line.
