# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 09:25:14 2019

@author: Julian Irwin

Notes on style:
    - Comment every class and function
    - Most functions should just do one little task
    - *Descriptive* variable names wherever possible: center_freq instead of fc
    - 

"""

from rtlsdr import RtlSdr
from scipy.fftpack import fft
from scipy import signal
import numpy as np

class SdrInterface(object):
    """Abstract class for interfacing with an SDR."""
    def __init__(self, center_freq, sample_freq, n_samples, modulation_freq, 
                 ppk_voltage, max_order):
        self.set_center_freq(center_freq)
        self.set_sample_freq(sample_freq)
        self.set_n_samples(n_samples)
        self.set_modulation_freq(modulation_freq)
        self.set_voltage(ppk_voltage)
        self.set_max_order(max_order)

        
    def set_center_freq(self, center_freq):
        """Set demodulator center freq."""
        self.center_freq = center_freq
        pass
    
    def set_sample_freq(self, sample_freq):
        """Set sampling freq."""
        self.sample_freq = sample_freq
        pass
    
    def set_n_samples(self, n_samples):
        """Set number of samples to acquire."""
        self.n_samples = n_samples
        self.fft_window = signal.blackmanharris(n_samples, sym=False)
        pass
    
    def set_modulation_freq(self, modulation_freq):
        """Set modulation freq."""
        self.modulation_freq = modulation_freq
        pass
    
    def set_voltage(self, ppk_voltage):
        """Set sampling driving voltage (peak to peak)."""
        self.ppk_voltage = ppk_voltage
        pass

    def set_max_order(self, max_order):
        """Set sampling driving voltage (peak to peak)."""
        self.max_order = max_order
        pass

    
    def get_samples(self):
        """
        Get self.num_samples samples, as a time series. Store as 
        self.time_series
        """
        pass
    
    def get_spectrum(self, subtract_bg=False):
        self.get_samples()  
        self.spectrum = np.roll(fft(self.time_series * self.fft_window),
                                self.n_samples//2)
        self.magnitude = np.abs(self.spectrum)
        self.phase = np.angle(self.spectrum)
        self.freqs = np.linspace(-self.sample_freq/2, self.sample_freq/2,  
                                 self.n_samples)
        
        # subtracting the background doesn't really do much
        if subtract_bg:
            bg_mag = self.bg_magnitude
            # don't subtract center peak
            center_index = self.n_samples//2
            bg_mag[center_index-100:center_index+100] = 0 
            self.magnitude = np.abs(self.magnitude - bg_mag)
        return self.freqs, self.magnitude, self.phase
    
    def get_bg_spectrum(self):
        """Collect a spectrum (experiment signal should be turned off) and
        store (and return) the magnitude (not phase...) as self.bg_magnitude.
        """
        
        #in the future, add some way to automatically turn the signal generator on and off
        self.get_samples()  
        self.spectrum = np.roll(fft(self.time_series * self.fft_window),
                                self.n_samples//2)
        self.bg_magnitude = np.abs(self.spectrum)
        return self.bg_magnitude
    
    def _nearest_ind(self, arr, val):
        return np.argmin(np.abs(arr - val))
    
    def find_peaks(self, width=100):
        """
        Indices of peaks up to modulation_freq*max_order
        Returned as ((i_0, i_0), (i_-1, i_+1), (i_-2, i_+2), ...) where i_n is
        the nth order peak, -n is -nth order peak.
        """
        max_order = self.max_order
        orders = np.arange(-max_order, max_order + 1)
        fis = [self._nearest_ind(i * self.modulation_freq, self.freqs) 
               for i in orders]
        mag = self.magnitude
        mi = [fi - width + np.argmax(mag[fi-width:fi+width]) for fi in fis]
        return np.array([(mi[max_order - i], mi[max_order + i]) 
                         for i in range(max_order + 1)])
    
    def plot_spectrum(self, ax, add_labels=True, add_peaks = True, show_bg = False,
                      **plot_kwargs):
        # Acquire data if none acquired yet
        if not hasattr(self, 'magnitude'):
            self.get_spectrum()
        m_db = 20 * np.log10(self.magnitude)
        ax.plot(self.freqs/1e3, m_db, 'g-', **plot_kwargs)
        xlim = (float(self.max_order)+1.1) * self.modulation_freq/1e3
        ax.set_xlim(-xlim, xlim)
        
        if add_peaks:
            ipeaks = self.find_peaks().flatten()
            ax.plot(self.freqs[ipeaks]/1e3, m_db[ipeaks], 'r*')
        if add_labels:
            ax.set_xlabel('f (kHz)')
            ax.set_ylabel('dB')
        if show_bg:
            bg_db = 20 * np.log10(self.bg_magnitude)
            ax.plot(self.freqs/1e3, bg_db, 'k-', alpha = 0.5)

        return self.freqs, self.magnitude, self.phase
    
    def peak_ratios(self, avg_posneg=True):
        """
        Find ratio of ith peak to 0th order peak.
        kwargs are passed to find peaks, so max_order=3 and width=100.
        
        Returns (peak1/peak0, peak2/peak0, ...) if avg_posneg = true.
        Returns ((peak-1/peak0, peak1/peak0), ...) if avg_posneg = false.
        """
        ipeaks = self.find_peaks()
        peak0 = self.magnitude[ipeaks[0][0]]
        peakratios = self.magnitude[ipeaks[1:]] / peak0
        if avg_posneg:
            return np.mean(peakratios, axis=1)
        else:
            return peakratios
    
    def get_sample_speed(self):
        """Calculate the speed amplitude of the sample from 
        the peak ratios, in SI units.
        
        Returns array of speeds at each harmonic
        """
        lambda_hene = 632.8e-9 #hene laser wavelength
        peakratios = self.peak_ratios()
        beta = 0.5*peakratios
        mod_freqs = (1+np.arange(len(beta)))*self.modulation_freq
        dev_freqs = mod_freqs*beta
        speed = dev_freqs*lambda_hene*0.5
        
        return speed
    
    def get_sample_displacement(self):
        """Calculate the dismplacement amplitude of the sample from 
        the sample speed, in SI units.
        
        Returns array of displacement at each harmonic
        """
        speed = self.get_sample_speed()
        #extra factor of 2pi comes from velocity integration, while in
        #get_sample_speed, only a ratio of frequencies was needed
        mod_freqs = 2*np.pi*(1+np.arange(len(speed)))*self.modulation_freq
        displacement = speed/(mod_freqs)
        
        return displacement
        
    def get_d33(self):
        """Calculates d33 in SI units from the peaks found in the spectrum
                
        Returns total d33, and an array of d33 values from individual harmonics
        """
        dis = self.get_sample_displacement()
        ampl_v = self.ppk_voltage/2.0
        rms_v = ampl_v/(np.sqrt(2.0))
        rms_dis = np.sqrt(0.5*np.sum(dis**2))
        total_d33 = rms_dis/rms_v
        d33 = dis/ampl_v
        
        return total_d33, d33

    def close(self):
        """Close hardware connection to sdr."""
        pass

class RtlSdrInterface(SdrInterface):
    """Interface to RtlSdr."""
    def __init__(self, center_freq, sample_freq, n_samples, modulation_freq,
                 ppk_voltage, max_order):
        self.sdr = RtlSdr()
        super().__init__(center_freq, sample_freq, n_samples, modulation_freq,
             ppk_voltage, max_order)
        
    def set_center_freq(self, center_freq):
        """Set demodulator center freq."""
        self.center_freq = center_freq
        self.sdr.center_freq = center_freq
        pass
    
    def set_voltage(self, ppk_voltage):
        """Set sample driving voltage."""
        self.ppk_voltage = ppk_voltage
        self.sdr.ppk_voltage = ppk_voltage
        pass
    
    def set_max_order(self, max_order):
        """Set sample driving voltage."""
        self.max_order = max_order
        self.sdr.max_order = max_order
        pass
    
    def set_sample_freq(self, sample_freq):
        """Set sampling freq."""
        self.sample_freq = sample_freq
        self.sdr.sample_rate = sample_freq
        pass
    
    def set_n_samples(self, n_samples):
        """Set sampling freq."""
        self.n_samples = n_samples
        self.fft_window = signal.blackmanharris(n_samples, sym=False)
        pass

    def get_samples(self):
        """Get N samples."""
        self.time_series = self.sdr.read_samples(self.n_samples)
        return self.time_series
    
    
    def close(self):
        """Close hardware connection to sdr."""
        self.sdr.close()
        
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    center_freq = 40e6
    sample_freq = 2.048e6
    n_samples = 2**21
    modulation_freq = 30e3
    ppk_voltage = 5
    max_order=3
    sdr = RtlSdrInterface(center_freq=center_freq, sample_freq=sample_freq, 
                          n_samples=n_samples, modulation_freq=modulation_freq,
                          ppk_voltage=ppk_voltage, max_order=max_order)
    f, m, _ = sdr.get_spectrum()
    fig, ax = plt.subplots(dpi=100)
    sdr.plot_spectrum(ax, add_peaks=(3, 100))
    plt.show()
    
   