"""
biosignal_simulator.py
----------------------
A simple EEG/biosignal simulator and visualizer.
Generates a synthetic signal, adds noise, applies a low-pass filter,
and plots all three stages side-by-side.

Libraries used: numpy, scipy, matplotlib, pathlib
"""


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import signal
from pathlib import Path


# 1.  Parameters
duration = 4         # seconds of signal to generate
fs = 256             # sampling rate (samples per second); typical EEG rate
freq_hz = 8          # signal frequency in Hz (8 Hz = alpha brain wave band)
amplitude = 1.0      # signal amplitude (height)
noise_level = 2.5    # how much random noise to add (higher = messier)
cutoff_hz = 15       # low-pass filter cutoff: keep freqs below this
filter_order = 4     # Butterworth filter order (higher = sharper cutoff)


# 2.  Generate clean signal
def generate_signal(duration, fs, freq, amplitude):
    t = np.linspace(0, duration, int(duration * fs), endpoint=False)
    clean_signal = amplitude * np.sin(2 * np.pi * freq * t)
    return t, clean_signal


# 3.  Add noise
def add_noise(clean_signal, noise_level, seed=42):
    rng = np.random.default_rng(seed)
    noise = noise_level * rng.standard_normal(len(clean_signal))
    return clean_signal + noise


# 4.  Apply a low-pass filter
def apply_lowpass_filter(noisy_signal, cutoff, fs, order):
    b, a = signal.butter(order, cutoff, btype='low', fs=fs)
    filtered = signal.filtfilt(b, a, noisy_signal)
    return filtered


# Visualize results
def plot_signals(t, clean, noisy, filtered, fs, freq):
    fig = plt.figure(figsize=(12, 8), facecolor='#fafafa')
    fig.suptitle(
        f'Biosignal Simulator - {freq} Hz signal, noise={noise_level}, cutoff={cutoff_hz} Hz',
        fontsize=14, fontweight='bold', y=0.98
    )

    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.55, wspace=0.35)

    colors = {
        'clean':    '#1D9E75',
        'noisy':    '#E24B4A',
        'filtered': '#534AB7',
        'spectrum': '#BA7517',
    }

    # Panel 1: clean signal
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(t, clean, color=colors['clean'], linewidth=1.2, label='Clean signal')
    ax1.set_title('1. Clean signal (synthetic sine wave)', fontsize=11)
    ax1.set_ylabel('Amplitude')
    ax1.legend(loc='upper right', fontsize=9)
    ax1.set_xlim(0, t[-1])
    ax1.grid(True, alpha=0.2)

    # Panel 2: noisy signal
    ax2 = fig.add_subplot(gs[1, :])
    ax2.plot(t, noisy, color=colors['noisy'], linewidth=0.8, alpha=0.85, label='Noisy signal')
    ax2.plot(t, clean, color=colors['clean'], linewidth=1.0, alpha=0.4, linestyle='--', label='Clean (reference)')
    ax2.set_title('2. After adding Gaussian noise', fontsize=11)
    ax2.set_ylabel('Amplitude')
    ax2.legend(loc='upper right', fontsize=9)
    ax2.set_xlim(0, t[-1])
    ax2.grid(True, alpha=0.2)

    # Panel 3: filtered signal
    ax3 = fig.add_subplot(gs[2, 0])
    ax3.plot(t, filtered, color=colors['filtered'], linewidth=1.2, label='Filtered signal')
    ax3.plot(t, clean, color=colors['clean'], linewidth=1.0, alpha=0.4, linestyle='--', label='Clean (reference)')
    ax3.set_title('3. After low-pass filter', fontsize=11)
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Amplitude')
    ax3.legend(loc='upper right', fontsize=9)
    ax3.set_xlim(0, t[-1])
    ax3.grid(True, alpha=0.2)

    # Panel 4: frequency spectrum (FFT)
    ax4 = fig.add_subplot(gs[2, 1])
    n_fft = len(noisy)
    freqs = np.fft.rfftfreq(n_fft, d=1/fs)          # frequency axis
    fft_mag = np.abs(np.fft.rfft(noisy)) / n_fft    # magnitutde spectrum

    ax4.plot(freqs, fft_mag, color=colors['spectrum'], linewidth=1.0)
    ax4.axvline(x=cutoff_hz, color='gray', linestyle='--', linewidth=0.8, label=f'Cutoff ({cutoff_hz} Hz)')
    ax4.set_title('4. Frequency spectrum (FFT)', fontsize=11)
    ax4.set_xlabel('Frequency (Hz)')
    ax4.set_ylabel('Magnitude')
    ax4.set_xlim(0, fs / 2)
    ax4.legend(loc='upper right', fontsize=9)
    ax4.grid(True, alpha=0.2)

    output_path = Path(__file__).parent / 'biosignal_output.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#fafafa')
    print("Plot saved to biosignal_output.png")
    plt.show()


# 6.  Main function
def main():
    print(f"Generating {freq_hz} Hz signal | duration={duration}s | fs={fs} Hz")

    t, clean = generate_signal(duration, fs, freq_hz, amplitude)
    noisy = add_noise(clean, noise_level)
    filtered = apply_lowpass_filter(noisy, cutoff_hz, fs, filter_order)

    # Quick stats pritned to terminal
    noise_rms = np.sqrt(np.mean((noisy - clean) ** 2))
    residual = np.sqrt(np.mean((filtered - clean) ** 2))
    improvement = (1 - residual / noise_rms) * 100

    print(f"Noise RMS error: {noise_rms:.4f}")
    print(f"Filtered RMS error: {residual:.4f}")
    print(f"Filter improvement: {improvement:.1f}%")

    plot_signals(t, clean, noisy, filtered, fs, freq_hz)

if __name__ == "__main__":
    main()
