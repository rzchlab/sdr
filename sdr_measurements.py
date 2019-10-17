# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 16:19:15 2019

@author: rzchlab
"""

import pandas as pd
import numpy as np


class BiasSweep(object):
    def __init__(self, sdr, fg):
        """
        Do a bias sweep sdr measurement

        Args:
            sdr (SdrInterface)
            fg (FuncGen)
        """
        self.sdr = sdr
        self.fg = fg
        # Don't hardcode these in case sdr.max_order changes
        peakcols = ['peak%d' % (i + 1) for i in range(self.sdr.max_order)]
        self.cols = ['bias_v', 'd33', 'speed', 'disp']
        self.data = pd.DataFrame(columns=self.cols + peakcols)

    def run(self, bias_voltages, back_to_zero=True):
        """
        Run a bias sweep measurement.

        Args:
            bias_voltages (list): List of the bias voltages to
                sweep through. The values are divided by 5 to account
                for the gain of the amplifier.
            back_to_zero (bool): If true, return bias to zero V 
                when sweep completed.
        """
        data = []
        for bv in bias_voltages:
            self.fg.offset(bv / 5)

            # Measure
            self.sdr.get_spectrum()
            d33, speed, disp = self.sdr.get_d33_spe_disp()
            peakratios = self.sdr.peak_ratios()
            data.append([bv, d33, speed, disp, *peakratios])

        # Return to starting postion
        if back_to_zero:
            self.fg.offset(0)

        peakcols = ['peak%d' % (i + 1) for i in range(self.sdr.max_order)]
        self.data = data
        outdf = pd.DataFrame(data=np.array(data), columns=self.cols + peakcols)
        self.data = outdf

    def triwave(self, step, nstep, add_final_zero=True):
        """
        Triangle wave points for use as the offsets in a bias sweep.

        Args:
            step (float): voltage step
            nstep (int): num steps per segment (1/4 wave). Total wavelength
                will be 4 * nstep, and +1` if add_final_zero
            add_final_zero (bool): if true, add a final zero to the wave
        """
        seg = np.arange(nstep) * step
        half = np.hstack((seg, nstep * step - seg))
        whole = np.hstack((half, -half))
        if add_final_zero:
            whole = np.hstack((whole, [0]))
        return whole


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

    def run(self, step_um, nsteps, moveaxis):
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
        self.data = data
        outdf = pd.DataFrame(data=np.array(data), columns=self.cols + peakcols)
        self.data = outdf


if __name__ == '__main__':
    class SdrMock(object):
        pass
    sdr = SdrMock()
    sdr.max_order = 3
    bs = BiasSweep(sdr, None)