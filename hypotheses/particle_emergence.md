# Hypotéza: Rovnoměrný výskyt kvazičástic (Homogeneous Quasiparticle Emergence)

## Autor / původ
T. Tříska (2025)

---

## Hypotéza
V systému Lineum se kvazičástice objevují **rovnoměrně** v prostoru i čase, pokud:
- není aplikována externí asymetrie (např. změna `KAPPA_MODE`),
- počáteční podmínky jsou náhodné, ale statisticky homogenní,
- dynamika probíhá v režimu bez výrazného gradientu φ.

Rovnoměrný výskyt znamená, že hustota detekovaných kvazičástic se v čase a mezi různými oblastmi liší jen v mezích statistické náhody.

---

## Stav testování
- 🔄 Testováno v bězích s různými semeny generátoru šumu (`LOW_NOISE_MODE` on/off).
- ✅ Dosavadní výsledky ukazují shodu rozložení s nulovým modelem (homogenní Poissonovo pole) v rámci statistické chyby.
- ⏳ Potřebné doplnění: systematické testy při jiných velikostech mřížky a délkách běhu.

---

## Metodika výpočtu

### Detekce a sběr dat
1. Běh simulace s definovaným počtem kroků a náhodnými počátečními podmínkami.
2. Detekce kvazičástic v každém kroku pomocí maxima amplitudy |ψ| nad zvoleným prahem.
3. Záznam souřadnic všech detekovaných kvazičástic v čase (`trajectories.csv`).

### Analýza rovnoměrnosti
4. Rozdělení pole na pravidelnou mřížku sektorů (např. 8×8).
5. Spočítání počtu částic v každém sektoru za celý běh.
6. Porovnání distribuce s teoretickou Poissonovou distribucí stejné střední hodnoty.
7. Výpočet chí-kvadrát statistiky nebo K–S testu pro kvantifikaci odchylek.

### Typické výstupy
- `particle_density_map.png` – mapa hustoty výskytu částic,
- `particle_distribution.csv` – histogram počtu částic v sektorech,
- `trajectories.csv` – úplný seznam poloh a časů výskytu.

---

## Význam
- **Základní metrika stability**: Rovnoměrný výskyt indikuje, že systém nevytváří preferované oblasti pro vznik částic.
- **Kontrolní test pro další hypotézy**: Slouží jako referenční chování, se kterým se porovnávají režimy s externími asymetriemi.
- **Vazba na statistickou mechaniku**: Potvrzení homogenity by znamenalo, že na velké škále se Lineum chová jako izotropní a homogenní médium.

---

## Doporučené další testy
- Opakovat měření pro různé velikosti mřížky a hustoty počátečního šumu.
- Ověřit, zda rovnoměrnost přetrvává při zavedení slabého gradientu φ.
- Testovat vliv délky běhu na statistickou stabilitu výsledků.

---

## Závěr
Hypotéza Rovnoměrného výskytu kvazičástic popisuje stav, kdy se kvazičástice objevují bez preferencí v prostoru a čase. Potvrzení této hypotézy by znamenalo, že v absenci vnějších vlivů je dynamika Linea statisticky homogenní a izotropní.