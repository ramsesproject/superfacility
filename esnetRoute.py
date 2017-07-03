from log import debugPrint
from log import addLogShowText
from collections import defaultdict
from heapq import *
import numpy as np
from simuPara import simuConfig as cfg

def dijkstra(edges, f, t):
    path_ret = list()
    g = defaultdict(list)
    for l,r,c in edges:
        g[l].append((c,r))

    q, seen = [(0,f,())], set()
    while q:
        (cost,v1,path) = heappop(q)
        if v1 not in seen:
            seen.add(v1)
            path = (v1, path)
            if v1 == t: 
                while len(path) > 0:
                    path_ret.append(path[0])
                    path = path[1]
                return (cost, path_ret[::-1])

            for c, v2 in g.get(v1, ()):
                if v2 not in seen:
                    heappush(q, (cost+c, v2, path))

    return (float("inf"), None)

'''
This is a model of data transfer service
'''
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
    ('LOND', 'AMST', 100, 82.347), ('AMST', 'CERN-272', 100, 79.924), ('CERN-272', 'CERN', 100, 52.821), ('CERN', 'CERN-513', 100, 61.500), 
    ('CERN-272', 'CERN-513', 100, 79.924), ('CERN-513', 'WASH', 100, 399.259), ('CERN-513', 'LOND', 100, 82.347), ('PNWG', 'LIGO', 10, 56.400), 
    ('PNNL', 'PNWG', 10, 55.200), ('SACR', 'PNWG', 100, 238.503), ('SACR', 'JGI', 10, 55.200), ('SACR', 'SNLL', 10, 65.386), 
    ('SACR', 'SUNN', 100, 150.000), ('LBL', 'SUNN', 100, 74.168), ('NPS', 'LBL', 1, 36.000), ('MSRI', 'LBL', 1, 39.628), 
    ('NERSC', 'SUNN', 100, 55.220), ('SLAC', 'SUNN', 100, 71.951), ('LLNL', 'SUNN', 100, 66.495), ('SAND', 'SUNN', 10, 117.000), 
    ('GA', 'SAND', 10, 55.220), ('ELPA', 'SUNN', 100, 326.484), ('ALBQ', 'ELPA', 100, 118.524), ('LANL', 'ALBQ', 100, 54.992), 
    ('KCP-ALBQ', 'ALBQ', 10, 56.643), ('SNLA', 'ALBQ', 10, 55.200), ('DENV', 'ALBQ', 100, 148.505), ('LSVN', 'DENV', 10, 141.508), 
    ('NSO', 'LSVN', 10, 58.512), ('IARC', 'LSVN', 1, 56.400), ('SACR', 'DENV', 100, 303.600), ('BOIS', 'DENV', 10, 236.519), 
    ('INL', 'BOIS', 10, 55.500), ('PNWG', 'BOIS', 10, 156.029), ('PNWG', 'DENV', 100, 385.134), ('NREL', 'DENV', 10, 42.000), 
    ('NGA-SW', 'DENV', 10, 58.024), ('PANTEX', 'DENV', 1, 56.643), ('KANS', 'DENV', 100, 138.000), ('KCP', 'KANS', 10, 41.587), 
    ('CHIC', 'KANS', 100, 110.400), ('HOUS', 'KANS', 100, 267.000), ('ELPA', 'HOUS', 100, 136.800), ('NASH', 'HOUS', 100, 162.778), 
    ('NASH', 'CHIC', 100, 148.505), ('STAR', 'CHIC', 100, 60.000), ('AMES', 'STAR', 100, 110.400), ('ANL', 'STAR', 100, 40.765), 
    ('FNAL', 'STAR', 100, 60.000), ('BOST', 'STAR', 100, 310.649), ('AOFA', 'STAR', 100, 284.727), ('ATLA', 'NASH', 100, 121.485), 
    ('SRS', 'ATLA', 1, 103.500), ('SRS-EM', 'ATLA', 1, 65.386), ('ORNL', 'ATLA', 100, 90.000), ('Y12', 'ORNL', 10, 40.765), 
    ('OSTI', 'ORNL', 10, 46.500), ('ORAU', 'ORNL', 10, 30.382), ('ETTP', 'ORNL', 10, 44.400), ('WASH', 'ATLA', 100, 188.496), 
    ('CHIC', 'WASH', 100, 233.892), ('JLAB', 'WASH', 10, 45.600), ('PPPL', 'WASH', 10, 58.500), ('AOFA', 'WASH', 100, 81.529), 
    ('LOND', 'AOFA', 100, 288.457), ('DOE-GTN', 'WASH', 1, 57.206), ('DOE-FORRESTAL', 'WASH', 1, 60.541), ('DOE-NNSA', 'WASH', 1, 72.000), 
    ('NEWY', 'AOFA', 100, 58.024), ('BOST', 'NEWY', 100, 117.000), ('PSFC', 'BOST', 10, 57.725), ('AMST', 'BOST', 10, 309.472), 
    ('LNS', 'BOST', 10, 56.106), ('BNL', 'NEWY', 100, 53.897), ('LOND', 'NEWY', 100, 247.218), ('AMST', 'LOND', 100, 82.347), 
    ('CERN-272', 'AMST', 100, 79.924), ('CERN', 'CERN-272', 100, 52.821), ('CERN-513', 'CERN', 100, 61.500), ('CERN-513', 'CERN-272', 100, 79.924), 
    ('WASH', 'CERN-513', 100, 399.259), ('LOND', 'CERN-513', 100, 82.347))

# distance information for routing
esnetVectorLength = [(x[0], x[1], x[3]) for x in esnetVector]
esnetVectorInfoDict = dict()
for e in esnetVector:
    esnetVectorInfoDict[(e[0], e[1])] = (e[2], e[3])

class esnetRoute(object):
    def __init__(self):
        super(esnetRoute, self).__init__()
        self.transfer        = list()            # a list of on-going transfers, should list all sites passby
        self.sites           = None
        self.state           = dict()            # current load, for convenience, orgornized as (s, e, n)
        self.time            = None              # current time

        _site = set()
        for link in  esnetVector:
            _site.add(link[0])
            _site.add(link[1])
        self.sites = list(_site)
    def update(self, t):
        self.time = t

    def finalizeTransfer(self, task):
        path = task.path
        for i in range(len(path)-1):
            v = (path[i], path[i+1])
            self.state[v] -= task.nStream
            if self.state[v] == 0: del self.state[v]

    def initTransfer(self, task):
        src, dst, nstream = task.expSite, task.compSite, task.nStream
        if src not in self.sites or dst not in self.sites:
            debugPrint("cannot find {0} or {1} in setup".format(src, dst))
            exit()
        path = dijkstra(esnetVectorLength, src, dst)[1]
        for i in range(len(path)-1):
            v = (path[i], path[i+1])
            if v in self.state:
                self.state[v] += nstream
            else:
                self.state[v]  = nstream
        task.path = tuple(path)
        # addLogShowText("Transfer")

    def weibull(self, x, a, b, c):
        return c * (x/a)**(b-1) * np.exp(-(x/a)**b)

    def cc2thr(self, cc, max_cc = 64):
        if cc >= max_cc:return 1.0 / (cc - max_cc+1)
        else: return 1.0 / max_cc * cc

    def availableBandwidth(self, task):
        min_bw = float('inf') + 1e12
        for i in range(len(task.path)-1):
            v = (task.path[i], task.path[i+1])
            _bw = cfg.esnetBWRatio * esnetVectorInfoDict[v][0] / self.state[v] * task.nStream
            # perc = self.weibull(self.state[v], 100, 1.5, 2.0)
            # _bw = 2.0 * esnetVectorInfoDict[v][0] * perc / self.state[v] * task.nStream
            min_bw = min(min_bw, _bw)

        return min_bw * 1e9 / 8

    def stateRecord(self, fp):
        for k in self.state:
            v = self.state[k]
            if fp is not None: 
                fp.write("{0}, {1}, {2}, {3}\n".format(self.time, k[0], k[1], v))
        return self.state