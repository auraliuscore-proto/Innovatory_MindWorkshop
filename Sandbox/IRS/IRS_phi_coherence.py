import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from pathlib import Path

# === Parametry sygnału ===
fs = 1000            # Hz
T = 5.0              # s
t = np.arange(0, T, 1/fs)

# Dwie składowe bazowe
f1 = 7.0             # Hz (pasmo niskie)
f2 = 13.0            # Hz (wyższe)
phi_shift = np.pi/6  # przesunięcie fazowe (symuluje "falowanie" między strumieniami)

# Sygnał A – mieszanka + szum
sigA = 0.9*np.sin(2*np.pi*f1*t) + 0.6*np.sin(2*np.pi*f2*t) + 0.3*np.random.randn(len(t))

# Sygnał B – podobny, ale z przesuniętą fazą i innym szumem
sigB = 0.9*np.sin(2*np.pi*f1*t + phi_shift) + 0.6*np.sin(2*np.pi*f2*t + phi_shift/2) + 0.3*np.random.randn(len(t))

# === Krótkookresowa koherencja (scipy.signal.coherence) ===
# Użyjemy okna 1 s (nperseg) – to odpowiada "slotowi"
nperseg = 1000
f, Cxy = signal.coherence(sigA, sigB, fs=fs, nperseg=nperseg)

# Prosta metryka "Φ-coherence": średnia ważona z pasma 5–15 Hz
band = (f >= 5) & (f <= 15)
phi_coherence = np.average(Cxy[band]) if np.any(band) else float('nan')

# === Wykres ===
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(f, Cxy)
ax.set_xlabel('Częstotliwość [Hz]')
ax.set_ylabel('Koherencja')
ax.set_title(f'IRS Φ-coherence (pasmo 5–15 Hz): {phi_coherence:.3f}')
ax.set_xlim(0, 60)
ax.grid(True, alpha=0.3)

# Katalog wyjściowy na artefakt
out_dir = Path("out/IRS")
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "irs_phi_coherence.png"
fig.tight_layout()
fig.savefig(out_path, dpi=150)
print(f"[OK] Zapisano wykres: {out_path}")
