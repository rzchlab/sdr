# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 13:53:01 2019

@author: rzchlab
"""

from rzcheasygui import Dialog

class SdrGUI():
    def __init__(self, sdr):
        self.sdr = sdr
        self.dmain = Dialog(title="SDR")        
        
        # Main tab
        self.tmain = self.dmain.tab('main')
        
        self.tmain.labelbox('Parameters')
        self.tmain.center_freq_Mhz = self.tmain.floatbox('Center Freq (MHz)', 40)
        self.tmain.sample_freq_Mhz = self.tmain.floatbox('Sample Freq (MHz)', 2.048)
        self.tmain.n_samples_log2 = self.tmain.integerbox('Samples 2^', 18)
        self.tmain.modulation_freq = self.tmain.floatbox('Modulation Freq (kHz)', 30)
        
        self.tmain.labelbox('')
        self.tmain.button('Get Spectrum', self.get_spectrum)
        
        self.tmain.graph = self.tmain.graph()
        
        self.tmain.labelbox('LDV Output')
        self.tmain.ldv_d33 = self.tmain.labelbox('d33: 0.0 pm/V')
        
    def get_spectrum(self):
        self.sdr.set_center_freq(int(self.tmain.center_freq_Mhz.get() * 1e6))
        self.sdr.set_sample_freq(int(self.tmain.sample_freq_Mhz.get() * 1e6))
        self.sdr.set_n_samples(2**self.tmain.n_samples_log2.get())
        ax = self.tmain.graph.ax[0]
        ax.cla()
        f, m, _ = self.sdr.plot_spectrum(ax)
        xlim = 4.1 * self.tmain.modulation_freq.get()
        ax.set_xlim(-xlim, xlim)
        ax.figure.canvas.draw()
        
        