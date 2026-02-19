# Tříska’s Spectral Mirror Hypothesis

## Autor

T. Tříska (2025)

## Stav

🧪 testováno – fáze párové spektrální analýzy

---

## Shrnutí

Tato hypotéza předpokládá, že některé výstupy systému Lineum představují **fázové zrcadlení** – jejich spektrum je inverzní, doplňující nebo interferenčně protilehlé vůči jinému výstupu.

Například `spec2_true` (κ = gradient) a `spec4_false` (κ = island) vykazují:

- blízké frekvenční pásmo (800–920 Hz po transformaci),
- vzájemné poměrové ladění (~1.048×),
- spektrální destruktivní interferenci při sloučení.

---

## Hypotéza

> Každý výstup systému Lineum má **potenciální zrcadlový obraz**,  
> který je spektrálně podobný, ale **fázově opačný** –  
> a tato zrcadla spolu interferují tak, že mohou zaniknout,  
> nebo vytvořit rovnovážný stav s minimální energetickou diverzí.

---

## Konkrétní případ

Pár `spec2_true` (gradient) a `spec4_false` (island):

- extrahované frekvenční řady byly laděny do stejného rozsahu (800–920 Hz),
- jejich jednotlivé frekvence se liší stabilně o ~4.8 %,
- při fázovém posunu `π` došlo k destruktivní interferenci,
- výstupní vlna rovnováhy vykazuje minimální spektrální rozdíl vůči oběma.

---

## Matematická formulace

Zrcadlový pár:

```
s₁(t) = sin(2πf₁t)
s₂(t) = sin(2πf₂t + π)
```

Rovnovážná vlna:

```
x(t) = s₁(t) + s₂(t) = sin(2πf₁t) + sin(2πf₂t + π)
```

Při `f₁ ≈ f₂` a fázovém posunu `π` vzniká interference:

```
x(t) ≈ 0  ⟹  destruktivní superpozice
```

---

## Spektrální důkaz

Bylo provedeno:

- spektrální porovnání výstupů pomocí Welchovy metody (`spectrum_difference_matrix.png`),
- konstrukce rušičky a rovnovážné vlny (`lineum_phase_filter_gradient_vs_island.wav`),
- poměrová analýza odpovídajících frekvencí.

Poměrové hodnoty frekvencí ukazují stabilní faktor `~1.048` napříč spektrem.

---

## Důsledky

- Existence spektrálních zrcadel implikuje **princip rovnováhy a kompenzace** v rámci Linea.
- Některé výstupy mohou být použity jako **protipól** jiného – tvoří harmonický pár.
- Rovnovážné výstupy jsou **emergentním výsledkem** interferenční superpozice.
