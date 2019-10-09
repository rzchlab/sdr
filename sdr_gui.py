# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 13:53:01 2019

@author: rzchlab
"""

from rzcheasygui import Dialog

class SdrGUI():
    def __init__(self, sdr, fg, mc):
        """
        Main GUI object.
        Args:
            sdr: SdrInterface instance
            fg: function generator instance from instrpyvisa
            mc: motion control instance from instrpyvisa
        """
        self.sdr = sdr
        self.fg = fg
        self.mc = mc
        self.dmain = Dialog(title="SDR")            
        self.PEAK_WIDTH_SEARCH = 100

        # SDR tab
        self.tmain = self.dmain.tab('SDR')
        
        self.tmain.labelbox('Parameters')
        self.tmain.center_freq_Mhz = self.tmain.floatbox('Center Freq (MHz)', 40)
        self.tmain.sample_freq_Mhz = self.tmain.floatbox('Sample Freq (MHz)', 2.048)
        self.tmain.n_samples_log2 = self.tmain.integerbox('Samples 2^', 18)
        self.tmain.modulation_freq = self.tmain.floatbox('Modulation Freq (kHz)', 30)
        self.tmain.ppk_voltage = self.tmain.floatbox('Voltage (Vpp)', 5)
        self.tmain.max_order = self.tmain.integerbox('Max order', 1)
        
        self.tmain.labelbox('')
        self.tmain.button('Get Spectrum', self.get_spectrum)
        self.tmain.button('Collect Background', self.get_bg_spectrum)
        self.tmain.show_bg = self.tmain.checkbox('Show Background', 0)
        
        self.tmain.graph = self.tmain.graph()
        
        self.tmain.labelbox('LDV Output')
        self.tmain.lbl_ldv_d33 = self.tmain.labelbox('d33: 0.0 pm/V')
        self.tmain.lbl_peak_ratios = self.tmain.labelbox('peak ratios: ')
        
        # FG tab
#        self.tfg = self.dmain.tab('SDR')
#        self.tfg.show_bg = self.tmain.checkbox('Show Background', 0)
                
        
    def get_bg_spectrum(self):
        self.sdr.set_center_freq(int(self.tmain.center_freq_Mhz.get() * 1e6))
        self.sdr.set_sample_freq(int(self.tmain.sample_freq_Mhz.get() * 1e6))
        self.sdr.set_n_samples(2**self.tmain.n_samples_log2.get())
        self.sdr.get_bg_spectrum()            

    def get_spectrum(self):
        self.sdr.set_modulation_freq(int(self.tmain.modulation_freq.get() * 1e3))
        self.sdr.set_center_freq(int(self.tmain.center_freq_Mhz.get() * 1e6))
        self.sdr.set_sample_freq(int(self.tmain.sample_freq_Mhz.get() * 1e6))
        self.sdr.set_n_samples(2**self.tmain.n_samples_log2.get())
        self.sdr.set_voltage(self.tmain.ppk_voltage.get())
        self.sdr.set_max_order(self.tmain.max_order.get())
        
        ax = self.tmain.graph.ax[0]
        ax.cla()
        self.sdr.get_spectrum()
        self.sdr.plot_spectrum(ax, show_bg = self.tmain.show_bg.get())
        ax.figure.canvas.draw()
        d33, _ = self.sdr.get_d33()
        s = 'peak ratios (ppm): ' + '{:.0f}  ' * self.tmain.max_order.get()
        peakratios = self.sdr.peak_ratios() * 1e6
        self.tmain.lbl_peak_ratios.set(s.format(*peakratios))
        self.tmain.lbl_ldv_d33.set(f'd33: {1e12*d33:.1f} pm/V')
        
        