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
