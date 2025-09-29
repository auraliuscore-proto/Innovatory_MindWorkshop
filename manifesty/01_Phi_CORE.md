# 🧩 Φ_CORE — rdzeń pojęć i metryk
> CC BY-SA 4.0 (docs). Celem Φ_CORE jest ujednolicenie pojęć, których używamy w projektach Innowatorium.

## 1. Pojęcia
- **Strumień** — sekwencja zdarzeń/sygnałów w czasie (ciąg lub okna).
- **Slot** — okno czasowe akumulacji sygnału (np. 1 s, 1 min).
- **Koherencja** — zgodność fazowo-częstotliwościowa pomiędzy strumieniami.
- **Rezonans** — wzmocnienie mocy w określonym paśmie i czasie.
- **Entropia rytmu** — miara nieuporządkowania wzorca czasowego.
- **Fingerprint fraktalny** — wizualny „odcisk” rytmu (skalowalny w czasie).

## 2. Metryki (wersja 0)
- **Φ-coherence(band)** — średnia koherencja w paśmie *(f_lo,f_hi)*.
- **R(band)** — rezonans: znormalizowana moc w paśmie / tło.
- **Hᵣ** — entropia rytmu (np. Shannon na histogramie interwałów).

## 3. Parametry referencyjne
- **fs** (Hz), **slot** (s), **pasma**: np. 5–15 Hz (demo).
- **Wizualizacja**: wykres koherencji, mapa rezonansu, fingerprint.

## 4. Artefakty i nazewnictwo
- `Public/reports/IRS_phi_coherence_YYYY-MM-DD.(png|json)`
- JSON zawiera: `date, metric, band_hz, value, fs, duration_s, notes`.

> Φ_CORE jest żywym dokumentem; zmiany tylko przez PR z krótkim uzasadnieniem.
