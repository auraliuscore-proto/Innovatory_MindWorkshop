# 🌀 IRS — Inteligentny Rezonans Strumieniowy

> **PL/EN manifest** — documentation is licensed under **CC BY-SA 4.0**; code under **GPL v3**.  
> Dokumentacja objęta licencją **CC BY-SA 4.0**, kod — **GPL v3**.

---

## 🧭 Idea / Idea

**PL:**  
IRS to ramowy model badawczo-eksperymentalny, w którym traktujemy strumienie danych, sygnałów i interakcji jak układy falowe. Szukamy **rezonansów** (wzmacniania), **dekoherencji** (tłumienia) i **wzorów fraktalnych** w czasie. Celem jest tworzenie wizualizacji, metryk i narzędzi, które pozwolą _zobaczyć_ i _modyfikować_ rytmy systemów złożonych (społecznych, informacyjnych, rynkowych, kreatywnych).

**EN:**  
IRS is a research/experimental framework that treats data streams and interactions as wave-like systems. We look for **resonances**, **decoherence**, and **fractal patterns** in time. The goal is to build visualizations, metrics and tools to _see_ and _shape_ the rhythms of complex systems (social, informational, market, creative).

---

## 🎯 Cele / Goals

- **Model** rezonansów i koherencji w strumieniach (czas, częstotliwość, faza).  
- **Wizualizacje**: pola, fraktale, mapy rytmów (Φ_CORE, sloty).  
- **Prototypy** algorytmów (Python/Notebooks + Actions).  
- **Etyka & prywatność**: anonimizacja, agregacja, jawność założeń.  
- **Repozytorium wiedzy**: wnioski, artefakty, dobra praktyka.

---

## 🧩 Architektura (wersja 0)

- **Rdzeń (Φ_CORE)** – wspólne pojęcia i metryki (koherencja, rezonans, entropia rytmu).  
- **Sloty czasowe** – okna obserwacji i akumulacji sygnału.  
- **Rdzenie IRS (IRS0..)** – wyspecjalizowane „perspektywy” analizy.  
- **Warstwa danych** – źródła, adaptery, polityka anonimizacji.  
- **Warstwa modeli** – transformacje (STFT/DFT), filtry, estymatory.  
- **Warstwa wizualizacji** – fraktale, mapy cieplne, diagramy fazowe.  
- **Warstwa automatyzacji** – GitHub Actions, generowanie raportów.

---

## 🔬 Zakres pierwszych eksperymentów

1. **IRS-Φ/koherencja** – metryka koherencji okien czasowych.  
2. **Mapy rezonansu** – heatmapa mocy w pasmach częstotliwości.  
3. **Fraktalne „odciski”** – wizualny fingerprint rytmu.  
4. **Raport cykliczny** – automatyczny PDF/MD z wykresami (Actions).

---

## 🧪 Technologia / Tech

- **Język:** Python (notebooks w `Sandbox/`), opcjonalnie R.  
- **Automatyzacja:** GitHub Actions.  
- **Wizualizacja:** matplotlib (bazowo), generatywne fraktale w `Wizualizacje/`.  
- **Dane:** tylko zanonimizowane / syntetyczne na starcie.

---

## 🔐 Prywatność i etyka

- Minimalizacja danych, anonimizacja, agregacja.  
- Transparentne założenia i parametry eksperymentów.  
- Dokumentowanie ograniczeń i ryzyk.

---

## 🗺️ Roadmap (M0 → M2)

- **M0 (ten PR):** Manifest + szkic metryk.  
- **M1:** Notebook `Sandbox/IRS/IRS_phi_coherence.ipynb` + przykładowe wykresy.  
- **M2:** Prosty pipeline Actions generujący raport tygodniowy.

---

## 📌 Status

Wersja 0 — dokument będzie ewoluować. Sugestie i PR mile widziane.

