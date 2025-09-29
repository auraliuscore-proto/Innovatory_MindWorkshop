import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from pathlib import Path
import json
from datetime import date

# === Parametry ===
fs = 1000
T = 5.0
t = np.arange(0, T, 1/fs)
today = date.today().isoformat()

# === Generowanie sygnałów ===
f1, f2 = 7.0, 13.0
phi_shift = np.pi/6

sigA = 0.9*np.sin(2*np.pi*f1*t) + 0.6*np.sin(2*np.pi*f2*t) + 0.3*np.random.randn(len(t))
sigB = 0.9*np.sin(2*np.pi*f1*t + phi_shift) + 0.6*np.sin(2*np.pi*f2*t + phi_shift/2) + 0.3*np.random.randn(len(t))

# === Koherencja ===
nperseg = 1000
f, Cxy = signal.coherence(sigA, sigB, fs=fs, nperseg=nperseg)
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

# === Ścieżki wyjściowe ===
reports_dir = Path("Public/reports")
reports_dir.mkdir(parents=True, exist_ok=True)

img_path = reports_dir / f"IRS_phi_coherence_{today}.png"
json_path = reports_dir / f"IRS_phi_coherence_{today}.json"

# === Zapis PNG ===
fig.tight_layout()
fig.savefig(img_path, dpi=150)
print(f"[OK] Zapisano wykres: {img_path}")

# === Zapis JSON ===
data = {
    "date": today,
    "metric": "IRS Φ-coherence",
    "band_hz": [5, 15],
    "value": round(float(phi_coherence), 3),
    "fs": fs,
    "duration_s": T,
    "notes": "Automatyczny raport IRS"
}
with open(json_path, "w", encoding="utf-8") as fjson:
    json.dump(data, fjson, ensure_ascii=False, indent=2)
print(f"[OK] Zapisano JSON: {json_path}")

