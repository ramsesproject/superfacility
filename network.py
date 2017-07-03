from log import debugPrint
import numpy as np
from simuPara import simuConfig as cfg
import os.path

esnetVector = (
    ('LIGO', 'PNWG', 10, 56.400), ('PNWG', 'PNNL', 10, 55.200), ('PNWG', 'SACR', 100, 238.503), ('JGI', 'SACR', 10, 55.200), 
    ('SNLL', 'SACR', 10, 65.386), ('SUNN', 'SACR', 100, 150.000), ('SUNN', 'LBL', 100, 74.168), ('LBL', 'NPS', 1, 36.000), 
    ('LBL', 'MSRI', 1, 39.628), ('SUNN', 'NERSC', 100, 55.220), ('SUNN', 'SLAC', 100, 71.951), ('SUNN', 'LLNL', 100, 66.495), 
    ('SUNN', 'SAND', 10, 117.000), ('SAND', 'GA', 10, 55.220), ('SUNN', 'ELPA', 100, 326.484), ('ELPA', 'ALBQ', 100, 118.524), 
    ('ALBQ', 'LANL', 100, 54.992), ('ALBQ', 'KCP-ALBQ', 10, 56.643), ('ALBQ', 'SNLA', 10, 55.200), ('ALBQ', 'DENV', 100, 148.505), 
    ('DENV', 'LSVN', 10, 141.508), ('LSVN', 'NSO', 10, 58.512), ('LSVN', 'IARC', 1, 56.400), ('DENV', 'SACR', 100, 303.600), 
    ('DENV', 'BOIS', 10, 236.519), ('BOIS', 'INL', 10, 55.500), ('BOIS', 'PNWG', 10, 156.029), ('DENV', 'PNWG', 100, 385.134), 
    ('DENV', 'NREL', 10, 42.000), ('DENV', 'NGA-SW', 10, 58.024), ('DENV', 'PANTEX', 1, 56.643), ('DENV', 'KANS', 100, 138.000), 
    ('KANS', 'KCP', 10, 41.587), ('KANS', 'CHIC', 100, 110.400), ('KANS', 'HOUS', 100, 267.000), ('HOUS', 'ELPA', 100, 136.800), 
    ('HOUS', 'NASH', 100, 162.778), ('CHIC', 'NASH', 100, 148.505), ('CHIC', 'STAR', 100, 60.000), ('STAR', 'AMES', 100, 110.400), 
    ('STAR', 'ANL', 100, 40.765), ('STAR', 'FNAL', 100, 60.000), ('STAR', 'BOST', 100, 310.649), ('STAR', 'AOFA', 100, 284.727), 
    ('NASH', 'ATLA', 100, 121.485), ('ATLA', 'SRS', 1, 103.500), ('ATLA', 'SRS-EM', 1, 65.386), ('ATLA', 'ORNL', 100, 90.000), 
    ('ORNL', 'Y12', 10, 40.765), ('ORNL', 'OSTI', 10, 46.500), ('ORNL', 'ORAU', 10, 30.382), ('ORNL', 'ETTP', 10, 44.400), 
    ('ATLA', 'WASH', 100, 188.496), ('WASH', 'CHIC', 100, 233.892), ('WASH', 'JLAB', 10, 45.600), ('WASH', 'PPPL', 10, 58.500), 
    ('WASH', 'AOFA', 100, 81.529), ('AOFA', 'LOND', 100, 288.457), ('WASH', 'DOE-GTN', 1, 57.206), ('WASH', 'DOE-FORRESTAL', 1, 60.541), 
    ('WASH', 'DOE-NNSA', 1, 72.000), ('AOFA', 'NEWY', 100, 58.024), ('NEWY', 'BOST', 100, 117.000), ('BOST', 'PSFC', 10, 57.725), 
    ('BOST', 'AMST', 10, 309.472), ('BOST', 'LNS', 10, 56.106), ('NEWY', 'BNL', 100, 53.897), ('NEWY', 'LOND', 100, 247.218), 
    ('LOND', 'AMST', 100, 82.347), ('AMST', 'CERN-272', 100, 79.924), ('CERN-272', 'CERN', 100, 52.821), 
    ('CERN', 'CERN-513', 100, 61.500), ('CERN-272', 'CERN-513', 100, 79.924), ('CERN-513', 'WASH', 100, 399.259), 
    ('CERN-513', 'LOND', 100, 82.347), ('NASH', 'WASH', 100, 200),
    ('APS', 'ANL', 100, 10), ('ALS', 'LBL', 100, 10), ('NSLS', 'BNL', 100, 10), ('SSRL', 'SLAC', 100, 10), \
    ('LCLS', 'SLAC', 100, 10), # make it huge for edge case
    ('APS', 'APS-C', 1e5, 10), ('ALS', 'ALS-C', 1e5, 10), ('NSLS', 'NSLS-C', 1e5, 10), ('SSRL', 'SSRL-C', 1e5, 10), \
    ('LCLS', 'LCLS-C', 1e5, 10))

def find_all_paths(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return [path]
    if not graph.has_key(start):
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths

def find_k_shortest_path(graph, start, end, k):
    paths = find_all_paths(graph, start, end, path=[])
    orderedpaths = sorted(paths, key=len)
    return orderedpaths[:min(k, len(orderedpaths))]

def find_shortest_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if not graph.has_key(start):
        return None
    shortest = None
    for node in graph[start]:
        if node not in path:
            newpath = find_shortest_path(graph, node, end, path)
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath
    return shortest

class networkConfig(object):
    euro = ("LOND", "AMST", "CERN", "CERN-272", "CERN-513")
    linkInfo = dict()
    for e in esnetVector:
        if e[0] in euro or e[1] in euro: continue      # avoid going through Europe
        linkInfo[(e[0], e[1])] = (cfg.net_ratio * e[2]*1e3/8, e[3])
        linkInfo[(e[1], e[0])] = (cfg.net_ratio * e[2]*1e3/8, e[3])

    net_graph = dict()
    for edge in esnetVector:
        if edge[0] in euro or edge[1] in euro: continue  # avoid going through Europe
        if net_graph.get(edge[0]) is None:net_graph[edge[0]] = set()
        if net_graph.get(edge[1]) is None:net_graph[edge[1]] = set()
        net_graph[edge[0]].add(edge[1])
        net_graph[edge[1]].add(edge[0])

    # creat a static table to save time on seaching path each time
    if os.path.isfile("end2endPath.npy"):
        end2endPath = np.load("end2endPath.npy")[()]
    else:
        end2endPath = dict()
        for src in cfg.expSiteName:                  
            for dst in cfg.compSiteName:
                if src == dst:continue
                # end2endPath[(src,dst)] = find_shortest_path(net_graph, src, dst)
                end2endPath[(src,dst)] = find_k_shortest_path(net_graph, src, dst, cfg.maxE2EPath)
        np.save("end2endPath", end2endPath)
                
    