# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 13:53:01 2019

@author: rzchlab
"""

from rzcheasygui import Dialog
import pandas as pd
from tkinter.filedialog import asksaveasfilename
import pickle

class SdrGUI():
    def __init__(self, sdr, fg, mc, linescan, biassweep):
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
        self.linescan = linescan
        self.biassweep = biassweep
        self.dmain = Dialog(title="SDR")
        self.PEAK_WIDTH_SEARCH = 100

        # SDR tab
        # --------------------
        self.tsdr = self.dmain.tab('SDR')

        self.tsdr.labelbox('Parameters')
        self.tsdr.center_freq_Mhz = self.tsdr.floatbox('Center Freq (MHz)', 40)
        self.tsdr.sample_freq_Mhz = self.tsdr.floatbox(
                'Sample Freq (MHz)', 2.048)
        self.tsdr.n_samples_log2 = self.tsdr.integerbox('Samples 2^', 18)
        self.tsdr.modulation_freq = self.tsdr.floatbox(
                'Modulation Freq (kHz)', 30)
        self.tsdr.ppk_voltage = self.tsdr.floatbox('Voltage (Vpp)', 1)
        self.tsdr.max_order = self.tsdr.integerbox('Max order', 1)
        self.tsdr.gain_level = self.tsdr.integerbox('Gain Level', 0)

        self.tsdr.labelbox('')
        self.tsdr.button('Get Spectrum', self.get_spectrum)
        self.tsdr.button('Collect Background', self.get_bg_spectrum)
        self.tsdr.show_bg = self.tsdr.checkbox('Show Background', 0)

        self.tsdr.graph = self.tsdr.graph()

        self.tsdr.labelbox('LDV Output')
        self.tsdr.lbl_ldv_d33 = self.tsdr.labelbox('d33: 0.0 pm/V')
        self.tsdr.lbl_peak_ratios = self.tsdr.labelbox('peak ratios: ')

        # FuncGen tab
        # --------------------
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

        # Motion Control tab
        # --------------------
        self.tmc = self.dmain.tab('Motion')
        self.tmc.labelbox('Configure')
        self.tmc.step_um = self.tmc.floatbox('Step (um)', 30)
        self.tmc.output_on = self.tmc.button(
                'Up', self.mc_mover_um(1, inv=True))
        self.tmc.output_on = self.tmc.button(
                'Down', self.mc_mover_um(1))
        self.tmc.output_on = self.tmc.button(
                'Left', self.mc_mover_um(2))
        self.tmc.output_on = self.tmc.button(
                'Right', self.mc_mover_um(2, inv=True))
        
        # Linescan tab
        # --------------------
        self.tls = self.dmain.tab('Linescan')
        self.tls.labelbox('Parameters')
        self.tls.step_um = self.tls.floatbox('Step (um)', 10)
        self.tls.nsteps = self.tls.integerbox('N Steps', 10)
        self.tls.moveaxis = self.tls.integerbox('Move Axis', 1)
        self.tls.labelbox('(y-axis is 1, x-axis is 2)')
        self.tls.button('Run Linescan', self.go_linescan)        
        self.tls.button(
                'Save Line Scan', lambda: self.go_save(self.linescan.data))
        self.tls.rb_labels = ['d33', 'speed', 'disp']
        self.tls.graph = self.tls.graph()
        cb = lambda: self.update_ls_plot(self.tls.graph)
        self.tls.rb = self.tls.radiobuttons(
                'Plot:', self.tls.rb_labels, 0, callback=cb)

        # Bias sweep tab
        # --------------------
        self.tbs = self.dmain.tab('BiasSweep')
        self.tbs.labelbox('Parameters')
        self.tbs.step_v = self.tbs.floatbox('Step (V)', 1)
        self.tbs.nsteps = self.tbs.integerbox('N Steps/Seg.', 10)
        self.tbs.labelbox('1 Seg = 1/4 wave')
        self.tbs.button('Run Bias Sweep', self.go_biassweep)
        self.tbs.button(
                'Save Bias Sweep', lambda: self.go_save(self.biassweep.data))
        self.tbs.rb_labels = ['d33', 'speed', 'disp']
        self.tbs.graph = self.tbs.graph()
        cb = lambda: self.update_bs_plot(self.tbs.graph)
        self.tbs.rb = self.tbs.radiobuttons(
                'Plot:', self.tbs.rb_labels, 0, callback=cb)

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
        self.sdr.set_gain_level(self.tsdr.gain_level.get())

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
        offset = self.tfg.offset.get()/5
        self.fg.setup_sin(freq, vpp, offset)
        self.sdr.set_modulation_freq(freq)
        self.sdr.set_voltage(vpp)

    def mc_mover_um(self, axis, inv=False):
        sgn = -1 if inv else 1
        return lambda: self.mc.move_um(axis, self.tmc.step_um.get() * sgn)

    def go_linescan(self):
        self.linescan.run(
                step_um=-self.tls.step_um.get(),
                nsteps=self.tls.nsteps.get(),
                moveaxis=self.tls.moveaxis.get())
        self.update_ls_plot(self.tls.graph)
        
    def go_save(self, df):
        filename = asksaveasfilename()
        df.to_csv(filename, sep='\t', float_format='%.6e', index_label='i')
        with open(filename+'.p', 'wb') as f:
            pickle.dump(obj=df, file=f)
#        pickle.dump(obj=df, file=filename)
        

    def go_biassweep(self):
        step = self.tbs.step_v.get()
        nsteps = self.tbs.nsteps.get()
        points = self.biassweep.triwave(step, nsteps, add_final_zero=True)
        self.biassweep.run(points)
        self.update_bs_plot(self.tbs.graph)

    def update_ls_plot(self, graph, i_ax=0):
        df = self.linescan.data
        icol = self.tls.rb.get()
        col = self.tls.rb_labels[icol]
        xlabel = 'Position (um)'
        xcol = 'loc_um'
        self.update_plot(graph, i_ax, df, xcol, col, icol, xlabel)
        
    def update_bs_plot(self, graph, i_ax=0):
        df = self.biassweep.data
        icol = self.tbs.rb.get()
        col = self.tbs.rb_labels[icol]
        xcol = 'bias_v'
        xlabel = 'Bias (V)'
        self.update_plot(graph, i_ax, df, xcol, col, icol, xlabel)

    def update_plot(self, graph, i_ax, df, xcol, col, icol, xlabel):
        ax = graph.ax[i_ax]
        ax.cla()
        unit_labs = ['pm/V', 'um/s', 'pm']
        unit_coef = [1e12, 1e6, 1e12]
        ax.plot(df[xcol] , df[col] * unit_coef[icol])
        ax.set_ylabel(col + ' ' + unit_labs[icol])
        ax.set_xlabel(xlabel)
        ax.figure.canvas.draw()       
