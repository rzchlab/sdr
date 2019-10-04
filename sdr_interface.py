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
    def __init__(self, center_freq, sample_freq, n_samples, modulation_freq):
        self.set_center_freq(center_freq)
        self.set_sample_freq(sample_freq)
        self.set_n_samples(n_samples)
        self.set_modulation_freq(modulation_freq)
        
    def set_center_freq(self, center_freq):
        """Set demodulator center freq."""
        self.center_freq = center_freq
        pass
    
    def set_sample_freq(self, sample_freq):
        """Set sampling freq."""
        self.sample_freq = sample_freq
        pass
    
    def set_n_samples(self, n_samples):
        """Set sampling freq."""
        self.n_samples = n_samples
        self.fft_window = signal.blackmanharris(n_samples, sym=False)
        pass
    
    def set_modulation_freq(self, modulation_freq):
        """Set sampling freq."""
        self.modulation_freq = modulation_freq
        pass
    
    def get_samples(self):
        """
        Get self.num_samples samples, as a time series. Store as 
        self.time_series
        """
        pass
    
    def get_spectrum(self):
        self.get_samples()  
        self.spectrum = np.roll(fft(self.time_series * self.fft_window),
                                self.n_samples//2)
        self.magnitude = np.abs(self.spectrum)
        self.phase = np.angle(self.spectrum)
        self.freqs = np.linspace(-self.sample_freq/2, self.sample_freq/2,  
                                 self.n_samples)
        return self.freqs, self.magnitude, self.phase
    
    def _nearest_ind(self, arr, val):
        return np.argmin(np.abs(arr - val))
    
    def find_peaks(self, max_order=3, width=100):
        orders = np.arange(-max_order, max_order + 1)
        fis = [self._nearest_ind(i * self.modulation_freq, self.freqs) 
               for i in orders]
        mag = self.magnitude
        mi = [fi - width + np.argmax(mag[fi-width:fi+width]) for fi in fis]
        return np.array([(mi[max_order - i], mi[max_order + i]) 
                         for i in range(max_order + 1)])
    
    def plot_spectrum(self, ax, add_labels=True, add_peaks=(3, 100), 
                      **plot_kwargs):
        # Acquire data if none acquired yet
        if not hasattr(self, 'magnitude'):
            self.get_spectrum()
        m_db = 20 * np.log10(self.magnitude)
        ax.plot(self.freqs/1e3, m_db, **plot_kwargs)
        if add_peaks:
            ipeaks = self.find_peaks(*add_peaks).flatten()
            ax.plot(self.freqs[ipeaks]/1e3, m_db[ipeaks], 'r*')
        if add_labels:
            ax.set_xlabel('f (kHz)')
            ax.set_ylabel('dB')
        return self.freqs, self.magnitude, self.phase
        
    def close(self):
        """Close hardware connection to sdr."""
        pass

class RtlSdrInterface(SdrInterface):
    """Interface to RtlSdr."""
    def __init__(self, center_freq, sample_freq, n_samples, modulation_freq):
        self.sdr = RtlSdr()
        super().__init__(center_freq, sample_freq, n_samples, modulation_freq)
        
    def set_center_freq(self, center_freq):
        """Set demodulator center freq."""
        self.center_freq = center_freq
        self.sdr.center_freq = center_freq
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
    sdr = RtlSdrInterface(center_freq=center_freq, sample_freq=sample_freq, 
                          n_samples=n_samples, modulation_freq=modulation_freq)
    f, m, _ = sdr.get_spectrum()
    fig, ax = plt.subplots(dpi=100)
    sdr.plot_spectrum(ax, add_peaks=(3, 100))
    plt.show()
    
   