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
        #--------------------
        self.tsdr = self.dmain.tab('SDR')
        
        self.tsdr.labelbox('Parameters')
        self.tsdr.center_freq_Mhz = self.tsdr.floatbox('Center Freq (MHz)', 40)
        self.tsdr.sample_freq_Mhz = self.tsdr.floatbox('Sample Freq (MHz)', 2.048)
        self.tsdr.n_samples_log2 = self.tsdr.integerbox('Samples 2^', 18)
        self.tsdr.modulation_freq = self.tsdr.floatbox('Modulation Freq (kHz)', 30)
        self.tsdr.ppk_voltage = self.tsdr.floatbox('Voltage (Vpp)', 5)
        self.tsdr.max_order = self.tsdr.integerbox('Max order', 1)
        
        self.tsdr.labelbox('')
        self.tsdr.button('Get Spectrum', self.get_spectrum)
        self.tsdr.button('Collect Background', self.get_bg_spectrum)
        self.tsdr.show_bg = self.tsdr.checkbox('Show Background', 0)
        
        self.tsdr.graph = self.tsdr.graph()
        
        self.tsdr.labelbox('LDV Output')
        self.tsdr.lbl_ldv_d33 = self.tsdr.labelbox('d33: 0.0 pm/V')
        self.tsdr.lbl_peak_ratios = self.tsdr.labelbox('peak ratios: ')
        
        # FG tab
        #--------------------
        self.tfg = self.dmain.tab('FuncGen')
        self.tfg.labelbox('Configure')
        self.tfg.vpp = self.tfg.floatbox('Vpp', 1)
        self.tfg.labelbox('(Including amp gain of 5x)')
        self.tfg.freq = self.tfg.floatbox('Freq (kHz)', 30)
        self.tfg.offset = self.tfg.floatbox('Offset (V)', 0)
        self.tfg.output_on = self.tfg.button('Config Sin', self.fg_setup_sin)
        
        self.tfg.labelbox('Output')
        self.tfg.output_on = self.tfg.button('On', fg.outp_on)
        self.tfg.output_off = self.tfg.button('Off', fg.outp_off)
        
        # FG tab
        #--------------------
        self.tmc = self.dmain.tab('Motion')
        self.tmc.labelbox('Configure')
        self.tmc.step_um = self.tmc.floatbox('Step (um)', 30)
        self.tmc.output_on = self.tmc.button('Up', 
                                             self.mc_mover_um(1, inv=True))
        self.tmc.output_on = self.tmc.button('Down', 
                                             self.mc_mover_um(1))
        self.tmc.output_on = self.tmc.button('Left', 
                                             self.mc_mover_um(2))
        self.tmc.output_on = self.tmc.button('Right', 
                                             self.mc_mover_um(2, inv=True))                
        
    def get_bg_spectrum(self):
        self.sdr.set_center_freq(int(self.tsdr.center_freq_Mhz.get() * 1e6))
        self.sdr.set_sample_freq(int(self.tsdr.sample_freq_Mhz.get() * 1e6))
        self.sdr.set_n_samples(2**self.tsdr.n_samples_log2.get())
        self.sdr.get_bg_spectrum()            

    def get_spectrum(self):
        self.sdr.set_modulation_freq(int(self.tsdr.modulation_freq.get() * 1e3))
        self.sdr.set_center_freq(int(self.tsdr.center_freq_Mhz.get() * 1e6))
        self.sdr.set_sample_freq(int(self.tsdr.sample_freq_Mhz.get() * 1e6))
        self.sdr.set_n_samples(2**self.tsdr.n_samples_log2.get())
        self.sdr.set_voltage(self.tsdr.ppk_voltage.get())
        self.sdr.set_max_order(self.tsdr.max_order.get())
        
        ax = self.tsdr.graph.ax[0]
        ax.cla()
        self.sdr.get_spectrum()
        self.sdr.plot_spectrum(ax, show_bg = self.tsdr.show_bg.get())
        ax.figure.canvas.draw()
        d33, _ = self.sdr.get_d33()
        s = 'peak ratios (ppm): ' + '{:.0f}  ' * self.tsdr.max_order.get()
        peakratios = self.sdr.peak_ratios() * 1e6
        self.tsdr.lbl_peak_ratios.set(s.format(*peakratios))
        self.tsdr.lbl_ldv_d33.set(f'd33: {1e12*d33:.1f} pm/V')

    def fg_setup_sin(self):
        """Wrapper for setting up sin output of fg"""
        vpp = self.tfg.vpp.get()/5
        freq = self.tfg.freq.get() * 1000
        offset = self.tfg.offset.get()
        self.fg.setup_sin(freq, vpp, offset)
        
    def mc_mover_um(self, axis, inv=False):
        sgn = -1 if inv else 1
        return lambda: self.mc.move_um(axis, self.tmc.step_um.get() * sgn)
        
        