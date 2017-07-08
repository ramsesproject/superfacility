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

### HPC utilization logs
This file save the utilization of HPC resource by events. It has two column (timeStamp,Nodes). Each line represent number of node availabe from current ___timeStamp___ to the ___timeStamp___ of next line.
