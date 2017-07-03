from expInstrument import expInstrument
from log import debugPrint
from simuPara import simuConfig as cfg

'''
This is a model for experiment instrument
'''
class experimentSite(object):
    def __init__(self, name, gbl_scheduler):
        super(experimentSite, self).__init__()
        self.jid          = 0
        self.name         = name                 # name a the facility, works as an identity
        self.instruments  = list()
        self.gbl_scheduler= gbl_scheduler

    def initInstrument(self):
        for g in cfg.beamlineCfg[self.name]:
            inst = expInstrument(self.name, g[0],  g[1],   g[2], self.gbl_scheduler, self.generateJID)
            self.instruments.append(inst)

    def startInstruments(self):
        for inst in self.instruments:
            inst.startRunExp()
            
    # use this function to provide unique job id for all instruments
    def generateJID(self):
        self.jid += 1
        return self.jid 