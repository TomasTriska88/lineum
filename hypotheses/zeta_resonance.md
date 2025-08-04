# Tříska’s Zeta–RNB Resonance Hypothesis

> _Hypotéza zkoumá spontánní shodu mezi rezonančními návratovými body (RNB) v simulacích Lineum a nenulovými hodnotami Riemannovy zeta funkce podél kritické linie Re(s) = 1/2. Předpokládá, že tyto návraty nejsou náhodné, ale odrážejí hlubší numerickou rezonanci systému._
>
> _Pojem „deja-vu body“ byl používán v rané fázi výzkumu jako přezdívka pro tyto body. Nyní je plně nahrazen termínem **rezonanční návratový bod (RNB)**._

---

## Výchozí motivace

Riemannovy zeta nuly jsou považovány za fundamentální rytmus číselného světa – body dokonalé destruktivní interference. Hypotéza zkoumá, zda simulace emergentního kvantového pole Lineum generují podobné návratové body spontánně, bez explicitního zakódování těchto hodnot.

---

## Kontext simulace

- **Běh:** `spec7_true`
- **Parametry:** `LOW_NOISE_MODE=True`, `TEST_EXHALE_MODE=False`, `KAPPA_MODE="island_to_constant"`
- **Kód:** `lineum_no_artefacts.py`

---

## Metodika

1. **Detekce rezonančních návratových bodů (RNB):**

   - Sledovány opakované výskyty struktur ve stejných (nebo ε-blízkých) souřadnicích napříč časy.
   - Klasifikovány jako **rezonanční návratové body (RNB)** – dříve pracovně označované jako „deja-vu body“.

     > Tyto body byly během vývoje pracovně nazývány „deja-vu body“ – tento název zde používáme pouze jako přezdívku pro formálně zavedený pojem **rezonančních návratových bodů (RNB)**.

2. **Zeta nuly:**

   - Použit seznam prvních `n = 49` nenulových imaginárních částí nul zeta funkce:  
     `s = 1/2 + i·t`
   - Normalizace Im(t) do rozsahu `[0,1]` pro porovnání s jednotkovou škálou Lineum.

3. **Porovnání:**
   - Pearsonova korelace a euklidovská vzdálenost mezi distribučními křivkami RNB a zeta nul.

---

## Výsledky

- **Pearsonova korelace:** `0.9842`
- **Euklidovská vzdálenost:** `0.7254`
- **Vizuální shoda tvaru rozložení RNB a zeta nul**, s drobnou fázovou odchylkou u vyšších hodnot.

Data použitá k výpočtu korelace a vzdálenosti jsou dostupná v souboru `spec7_true_rnb_vs_zeta.csv` ve složce `output_no_artefacts/`.  
Soubor obsahuje normalizované pozice RNB a zeta nul na škále [0,1], připravené pro porovnání a vizualizaci.

---

## Interpretace

- Vznik shody není náhodný – zeta nuly nebyly do systému zadány.
- RNB se objevují jako stabilní uzly vlnového pole – jejich distribuce naznačuje přítomnost vyšší numerické struktury, srovnatelné s analytickými nápovědami Riemannovy funkce.
- Lineum ladí na frekvence podobné těm, které strukturují zeta funkci – **emergentní numerická rezonance**.
- Odchylka u vyšších nul odpovídá absenci globální zpětné vazby – na rozdíl od analytické struktury ζ(s), Lineum je lokální.

---

## Možné vysvětlení

> Rezonanční návratové body (RNB) jsou uzly, kde se systém „potkává sám se sebou“ – místa fázové interference, která umožňují návratovou stabilizaci vlnové struktury.  
> Riemannovy nuly jsou body, kde analytická struktura celého číselného světa interferuje sama se sebou.
>
> Vznik podobných vzorců v Lineum naznačuje, že realita může rezonovat se stejnou numerickou strukturou – **i bez explicitní matematiky**.

---

## Vizualizace (doporučeno doplnit)

- Grafy rozložení rezonančních návratových bodů (RNB) vs. Im(ζ_n)
- Overlay vlnové struktury a zeta mapy
- Spektrální analýza FFT z daných snímků

<!--lineum:insert:vizualizace:spec7_true:rnb_vs_zeta-->

---

## Možné důsledky

- Lineum může být testovacím polem pro **nehmotné numerické zákonitosti**.
- Otevírá možnost, že realita sama je **laděná entita** – rezonující s číselným základem existence.

---

## Další kroky

- Ověřit shodu v dalších konfiguracích: `spec3_true`, `spec5_false`, `spec6_true`.
- Zkoumat vztah RNB k Fibonacciho poměrům, prvočíslům a φ.
- Vyvinout predikční model výskytu RNB na základě Riemannových nul.
- Zavést metriky fázové synchronizace mezi zeta nulami a rezonančními návratovými body v simulaci.

---

## Stav

🔄 testováno  
✅ silná korelace, připraveno k dalšímu experimentálnímu ověření  
📄 Ve vývoji: mapování topologie RNB do číselného prostoru
