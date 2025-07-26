# 🧪 Lineum – Seznam úkolů pro další ověření

Tento soubor obsahuje přehled výzkumných bodů, které vyžadují další testování, vizualizaci nebo kvantitativní ověření. Každý bod by měl být buď potvrzen simulací, nebo jednoznačně formulován jako hypotéza.

---

## ✅ Již potvrzené výpočtem / animací

- Detekce vírů (vortex_log.csv)
- Topologický náboj (topo_log.csv)
- Spin a fázový tok (frames_curl.npy, lineum_flow.gif)
- Stabilita φ-pastí (phi_center_log.csv, φ animace)
- Vznik kvazičástic a jejich trajektorie (trajectories.csv)
- Odezva φ na |ψ|² (φ rovnice, vizuálně potvrzeno)

---

## 🟡 Potřebuje ověření / doplnění

### 🔲 1. Reorganizace kvazičástic v hmotném objektu
- Simulovat shluk kvazičástic, sledovat deformaci při pohybu k φ-maximu
- Porovnat tvar a polohu shluku v čase
- [ ] Vizualizace přeskupení |ψ| a overlay s φ

### 🔲 2. Rychlost přiblížení objektů podle „hmotnosti“
- Ověřit, zda menší objekty reagují rychleji
- Kvantifikovat přes trajektorie a φ-centrické měření
- [ ] Spustit simulaci s 2–3 shluky různé hustoty

### 🔲 3. Vzájemné ovlivnění více φ-pastí
- Analyzovat slučování, interferenci nebo stabilitu více maxim
- [ ] Vizualizace rozdělených φ-center ve stejném běhu

### 🔲 4. Přitažlivost bez síly – emergentní tok
- Ověřit, zda vzniká tok ψ směrem k φ bez síly


- [ ] Porovnat ∇arg(ψ) a gradient ϕ
### 🔲 5. Vztah lineum k matematickým konstantám
- Ověřit, zda vztah lineum ke zlatému řezu (φ) se projevuje ve struktuře pole nebo emergentních jevech
- Ověřit vztah lineum k Fibonacciho posloupnosti (například distribuce počtu linonů)
- Ověřit, zda existuje souvislost lineum s Ludolfovým číslem π (např. v oscilacích nebo topologii)

---

## 🔎 Poznámky

- Každý bod by měl mít vlastní podložení ve výstupu (csv, animace, snímky).
- Hotové body přesuneme nahoru do „již potvrzené“ části.
- Pokud se hypotéza ukáže jako chybná, přemístíme ji do archivu (hypothesis_archive.md).

