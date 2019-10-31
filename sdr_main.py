# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 13:51:02 2019

@author: rzchlab
"""

from sdr_interface import RtlSdrInterface
from sdr_gui import SdrGUI
from sdr_measurements import LineScan, BiasSweep, BiasSweepWithCV
from instrpyvisa import (FuncGenAgilent33220, MotionControllerNewportESP300, 
                         LockInAmpSrs830)
from visa import ResourceManager

######################
###      TODO      ###
######################
"""
- Add cycles to biassweep
- Email / text alerts?
- Autosave data to temp files
- Add CV loop units
- peak heights from peak fits instead of just peak values in sdr spectra
- allow for multiple sdr spectra per point, then take statistics
- method for measuring when mod index isn't << 1?
- check with laser stabilization?
    - (Should make guide for how to do this)

"""


#####################
### CONFIGURATION ###
#####################

FG_ADDRESS = 10
MC_ADDRESS = 20
LIA_ADDRESS = 9

######################
### INITIALIZATION ###
######################

rm = ResourceManager()
fg = FuncGenAgilent33220(FG_ADDRESS, rm)
mc = MotionControllerNewportESP300(MC_ADDRESS, rm)
sdr = RtlSdrInterface(40e6, 2.048e6, 512**2, 30e3, 1, 1)
lia = LockInAmpSrs830(LIA_ADDRESS, rm)

linescan = LineScan(sdr, fg, mc)
biassweep = BiasSweep(sdr, fg)
biassweepcv = BiasSweepWithCV(sdr, fg, lia)


######################
###      MAIN      ###
######################

gui = SdrGUI(sdr, fg, mc, lia, linescan, biassweep, biassweepcv)
gui.dmain.show()