# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 13:51:02 2019

@author: rzchlab
"""

from rzcheasygui import Dialog
from sdr_interface import RtlSdrInterface
from sdr_gui import SdrGUI
from sdr_measurements import LineScan
from instrpyvisa import FuncGenAgilent33220, MotionControllerNewportESP300
from visa import ResourceManager

#####################
### CONFIGURATION ###
#####################

FG_ADDRESS = 10
MC_ADDRESS = 20

######################
### INITIALIZATION ###
######################

rm = ResourceManager()

fg = FuncGenAgilent33220(FG_ADDRESS, rm)
mc = MotionControllerNewportESP300(MC_ADDRESS, rm)
sdr = RtlSdrInterface(40e6, 2.048e6, 512**2, 30e3, 5, 1)

linescan = LineScan(sdr, fg, mc)


######################
###      MAIN      ###
######################

gui = SdrGUI(sdr, fg, mc, linescan)
gui.dmain.show()