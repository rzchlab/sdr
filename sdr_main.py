# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 13:51:02 2019

@author: rzchlab
"""

from rzcheasygui import Dialog
from sdr_interface import RtlSdrInterface
from sdr_gui import SdrGUI

sdr = RtlSdrInterface(40e6, 2.048e6, 512**2, 30e3)

hooks = {'get_spectrum': lambda: None}

gui = SdrGUI(sdr)
gui.dmain.show()