# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 16:19:15 2019

@author: rzchlab
"""

import pandas as pd
import numpy as np

class LineScan(object):
    def __init__(self, sdr, fg, mc):
        """
        Do a line scan sdr measurement
        
        Args:
            sdr (SdrInterface)
            fg (FuncGen)
            mc (MotionController)
        """
        self.sdr = sdr
        self.mc = mc
        self.fg = fg
        # Don't hardcode these in case sdr.max_order changes
        peakcols = ['peak%d' % (i + 1) for i in range(self.sdr.max_order)]
        self.cols = ['loc_um', 'd33', 'speed', 'disp']
        self.data = pd.DataFrame(columns=self.cols + peakcols)
        
    def main(self, step_um, nsteps, moveaxis):
        """
        Run a linescan measurement.
        
        Args:
            step_um (float): Micron step size
            nsteps (int): Number of steps. Num measurements is nsteps + 1.
            moveaxis (int): Motion controller axis to move
        
        For now, assume that the FuncGen is already setup with proper
        parameters and SdrInterface is already setup properly.
        """
        
        data = []
        
        # Take first point
        self.sdr.get_spectrum()
        d33, speed, disp = self.sdr.get_d33_spe_disp()
        peakratios = self.sdr.peak_ratios()
        data.append([0.0, d33, speed, disp, *peakratios])
        
        # Loop through rest of points
        for i in range(nsteps):
            # Move
            self.mc.move_um(moveaxis, step_um)
            loc = (i + 1) * step_um
                
            # Measure
            self.sdr.get_spectrum()
            d33, speed, disp = self.sdr.get_d33_spe_disp()
            peakratios = self.sdr.peak_ratios()
            data.append([loc, d33, speed, disp, *peakratios])
            
        # Return to starting postion
        self.mc.move_um(moveaxis, -step_um * nsteps)
        
        peakcols = ['peak%d' % (i + 1) for i in range(self.sdr.max_order)]
        print(self.sdr.max_order, peakcols)
        self.data = data
        print(len(data))
        print(len(data[0]))
        print(self.cols + peakcols)
        outdf = pd.DataFrame(data=np.array(data), columns=self.cols + peakcols)
        self.data = outdf
        
        