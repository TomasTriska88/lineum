import { writable, derived } from 'svelte/store';

export const translations = {
    cs: {
        meta: {
            title: "Lineum | Dynamika diskrétních polí",
            description: "Spojitý fyzikální engine generující inteligenci a logiku z emergentních vlnových polí."
        },
        common: {
            brand: "Lineum",
            beta: "BETA"
        },
        nav: {
            portal: "Portál",
            lab: "Laboratoř",
            api: "API Řešení",
            wiki: "Wiki / Science",
            support: "Podpora",
            about: "O Nás"
        },
        hero: {
            headline: "Objevte strukturu samotného prostoru.",
            subheadline: "Hardware bez tranzistorů. Computace, která nepočítá, ale roste s vesmírem.",
            cta_api: "VSTUP DO API",
            cta_lab: "SIMULAKRUM A LAB",
            symbol: "Λ",
            title_prefix: "Věda o polích, která ",
            title_highlight: "dýchají.",
            subtitle: "Lineum je zkoumáním kontinuálních prostorových výpočtů. Studujeme, jak jednoduchá deterministická fyzika dává vzniknout inteligentnímu chování.",
            cta_wiki: "Prozkoumat Wiki",
            cta_audit: "Audit Důkazů"
        },
        sections: {
            layman: {
                label: "Filosofie",
                title: "Inteligence z jednoduchosti",
                p1: "Namísto programování explicitních pravidel nebo trénování masivních neuronových sítí pokládá Lineum jinou otázku: Co kdyby výpočty mohly přirozeně vyplynout z fyziky kontinuálního prostoru?",
                p2: "Návrhem specifického matematického prostředí (Rovnice Eq-4) pozorujeme spontánní formování stabilních částicových struktur, které přirozeně hledají optimální cesty svým okolím.",
                visual_label: "Jádrová interakce"
            },
            scientist: {
                label: "Pro výzkumníky",
                title: "Rigorózní ověřování",
                whitepaper: {
                    title: "The Core Paper",
                    desc: "Přečtěte si základní dokument definující Eq-4, strukturální parametry a dynamiku kvazičástic.",
                    link: "Číst Whitepaper →"
                },
                zenodo: {
                    title: "Otevřený archiv dat",
                    desc: "Získejte přístup k našim kanonickým běhům, metadatům a matematickým důkazům v repozitáři Zenodo.",
                    link: "Přejít na Zenodo →"
                },
                simulacrum: {
                    title: "Interaktivní Simulakrum",
                    desc: "Živé WebGL prostředí pro testování parametrů a přímé pozorování interakcí pole v prohlížeči.",
                    link: "Spustit Simulakrum →"
                },
                referencePack: {
                    title: "Referenční implementace",
                    desc: "Stáhněte si zdrojové kódy a reprodukční skripty pro nezávislé ověření našich tvrzení na vlastním hardwaru.",
                    link: "Zobrazit na GitHubu →"
                }
            }
        },
        legend: {
            trigger_label: "Mechanika pole",
            title: "Telemetrie Simulace",
            subtitle: "Živé strukturální proměnné",
            items: {
                psi: {
                    label: "ψ Fáze (Kvazičástice)",
                    description: "Hlavní entity mřížky. Tyto samoorganizující se shluky energie se chovají jako částice a navigují prostorem podle jasných deterministických pravidel."
                },
                kappa: {
                    label: "κ Prostředí (Substrát)",
                    description: "Statický terén. Pevné hranice a zóny vysokého tření, které formují pohyb částic po mřížce."
                },
                phi: {
                    label: "φ Paměť (Tenze)",
                    description: "Strukturální paměť. Pohybující se částice zanechávají dočasnou fyzickou 'stopu', která odpuzuje ostatní od následování stejné trasy."
                },
                warp: {
                    label: "Topologický Warp (Navádění)",
                    description: "Dynamické zakřivení pole. Ukazuje nejstrmější klesání k optimálním cílům a vede částice jako gravitační tah."
                }
            },
            invitation: "Lineum je plně deterministické. To, co vypadá jako 'rozhodování', je pouze sestup po vlastnoručně generovaném gradientu.",
            faq: [
                {
                    q: "Je to AI neuronová síť?",
                    a: "Ne. Lineum používá spojité vlnové rovnice (Eq-4), žádné diskrétní váhy ani trénovací data. 'Inteligence' vyvstává přirozeně z fyziky pole, které reaguje s překážkami."
                },
                {
                    q: "Co je to 'linon'?",
                    a: "Linon je lokalizovaný shluk vlnové energie, který si při pohybu udržuje svůj tvar. Představte si je jako digitální kapky navigující mikroskopickou krajinou ke svému cíli."
                },
                {
                    q: "Proč na tom záleží?",
                    a: "Když pochopíme, jak příroda řeší prostorové problémy skrze dynamiku kapalin, můžeme vybudovat fundamentálně nové přístupy k routování, logistice a simulacím."
                }
            ]
        },
        footer: {
            copy: "© 2026 Tým Lineum. Vydáno pro vědecké a výzkumné účely.",
            support: "Podpořit projekt (Revolut)",
            github: "GitHub",
            privacy: "Zásady Ochrany Osobních Údajů"
        },
        lina: {
            clear_history: "Vymazat historii",
            clear_history_title: "Smazat neuronové spojení?",
            confirm_delete: "Potvrdit smazání",
            cancel: "Zrušit",
            clear_history_body: "Tímto trvale vymažete veškerý aktuální kontext a paměť relace.",
            welcome_title: "Výzkumné spojení navázáno",
            welcome_body: "Mohu pro vás analyzovat whitepapery a logiku simulace. Jak vám dnes mohu pomoci s výzkumem?",
            show_previous: "Zobrazit předchozí kontext",
            hidden: "skryto",
            recharging: "Nabíjení",
            auto_retry: "Auto-Retry",
            retry_now: "Zkusit znovu",
            placeholder: "Zeptejte se Liny na cokoliv...",
            stop_audio: "Zastavit zvuk",
            status_idle: "Klikněte pro spuštění Liny ✨",
            status_active: "SPOJENÍ AKTIVNÍ",
            privacy: "Lina je výzkumný nástroj. Anonymizované konverzace mohou být ukládány.",
            insight_header: "PRŮZKUMNÍKŮV VZHLED"
        },
        wiki: {
            hints: {
                vortex: "✨ Lina: Představ si Linony jako bubliny ve vodě—stále se hýbou, ale drží si svůj tvar. Jsou to 'atomy' naší simulace.",
                psi: "✨ Lina: Psi je tady hlavní 'herec'. Říká nám, kde se v daný moment odehrává děj.",
                kappa: "✨ Lina: Kappa je naše ladící mapa. Je to jako terén, který určuje, jak rychle řeka na různých místech teče.",
                faq_physics: "✨ Lina: I když to vypadá jako fyzika, Lineum je spíš digitální umělecké dílo řízené matematikou. Fyzikální pojmy používáme, protože k tomu sedí!"
            }
        },
        support: {
            title: "Podpořte projekt Lineum",
            subtitle: "Posouváme hranice dynamiky diskrétních polí skrze otevřený výzkum.",
            description: "Lineum je nezávislý výzkumný projekt věnovaný objevování fundamentálních pravidel emergentních spojitých excitací. Vaše podpora pomáhá hradit výpočetní náklady simulací, udržovat naši open-source infrastrukturu a dává nám více času na vědeckou analýzu.",
            goals: {
                infrastructure: {
                    title: "Výpočetní Infrastruktura",
                    desc: "Financování serverů s vysokou dostupností pro auditní běhy a dlouhodobou archivaci."
                },
                opensource: {
                    title: "Open Source Vývoj",
                    desc: "Podpora vývoje nástrojů jako je Simulakrum a jádro Lineum."
                },
                research: {
                    title: "Nezávislý Výzkum",
                    desc: "Zajištění, že tato práce zůstane otevřená, ověřitelná a nezávislá na vnějších omezeních."
                }
            },
            cta_label: "Přispět přes Revolut"
        },
        whitepaper_warning: {
            title: "Živý výzkum / Mezera v dokumentaci",
            paragraphs: [
                "Vezměte prosím na vědomí, že <b>Lineum je neustále se vyvíjející výzkumný projekt</b>. Statické whitepapery zde mohou zaostávat za nejnovějšími daty z auditů a experimentů.",
                "Pro nejaktuálnější představu doporučujeme <a href='/api-solutions' style='color: var(--accent-color); text-decoration: underline;'>zhlédnout naši ukázku Swarm Routing</a>. Slouží jako živý důkaz našich tvrzení, umožňující pozorovat spojitou dynamiku polí a emergentní částice na vlastní oči.",
                "Případně se můžete <b>zeptat Liny</b> (naší AI asistentky). Má přístup k nejnovějšímu kontextu, výsledkům auditů a reformulovaným hypotézám, které zde ještě nemusí být textově zaneseny.",
                "Používejte tyto dokumenty jako základní reference, ale věřte živým datům a Lině stran aktuálního stavu výzkumu."
            ],
            ack_label: "Rozumím, pokračovat"
        },
        api_solutions: {
            hero: {
                domain: "SPECIALIZOVANÁ DOMÉNA",
                title: "Fluidní výpočetní API pro<br class='hidden sm:block' /> prostorovou umělou inteligenci.",
                highlight: "True RNG. Hašování. LPL Logika.",
                subtitle: "Integrujte plně deterministickou matematiku fyzikální interference do vašeho B2B stacku. Využitím hraničních fázových přechodů ('Edge-of-Chaos') můžete nahradit tradiční diskrétní algoritmy přirozeným prostorovým výpočtem.",
                cta_build: "Začít Stavět",
                cta_docs: "Přečíst Dokumentaci"
            },
            roi: {
                title: "Neuromorfní ekosystém AI",
                subtitle: "Lineum představuje revoluční ne-von-Neumannovskou architekturu. Prostřednictvím výpočtů založených čistě na interferenci vln odemykáme <strong class='text-white font-semibold'>absolutní náhodnost (True RNG), nevratné hašování a LPL překladače</strong>. Nevyžaduje se žádný trénink neuronových sítí."
            },
            features: {
                rng: {
                    title: "Těžba True RNG",
                    desc: "Generuje matematicky dokonalou náhodnost zesílením kvantového a termálního šumu procesorů na samou hranici chaosu."
                },
                hash: {
                    title: "Kryptografická lavina",
                    desc: "Jednosměrné hardwarové hašování. Změna jediného bytu nevyhnutelně spouští masivní topologické makro-fraktury."
                },
                lpl: {
                    title: "Vizuální logická hradla",
                    desc: "Nahrajte strukturální CAD masku. Pohybující se vlny zkompilují univerzální logiku čistě skrze geometrické odrazy (bez jakéhokoliv učení)."
                }
            },
            usecases: {
                lpl: {
                    label: "PŘÍPADOVÁ STUDIE 01",
                    title: "Lineum Polygon<br />Language (LPL)",
                    desc: "Zapomeňte na statisíce hodin trénování neuronových sítí. Pomocí LPL jednoduše zkompilujete CAD návrh. Fyzikální fluidní engine přirozeně spočítá libovolná logická hradla a obvody čistě dynamikou vlnění.",
                    bullet1_title: "Inteligentní Zero-Training",
                    bullet1_desc: "Vyhodnocuje výpočetní logiku vizuálně formou geometrie.",
                    bullet2_title: "Geometrická telemetrie",
                    bullet2_desc: "Získávejte raw parametry matematické interference v JSON výstupu."
                },
                rng: {
                    label: "PŘÍPADOVÁ STUDIE 02",
                    title: "True RNG a<br />Zbytková entropie",
                    desc: "Lineum rovnice operující těsně pod hranicí fázového přesycení zesiluje mikroskopické odchylky v časování procesoru do masivních turbulencí. Vytváří tak dokonalá náhodná čísla a nevratné kryptografické otisky.",
                    bullet1_title: "Těžba absolutní entropie",
                    bullet1_desc: "Nezávisí na žádných deterministických pseudo-vzorcích.",
                    bullet2_title: "Destruktivní lavinový efekt",
                    bullet2_desc: "Minimální odlišnost na vstupu způsobuje geometrickou explozi vzorce."
                }
            },
            demos: {
                title: "Live Interaktivní Prototypy",
                desc: "Experimentujte s tenzorovým enginem Lineum Core přímo ve vašem prohlížeči."
            },
            domains: {
                title: "Objevujte aplikované domény",
                desc: "Rovnice Lineum je zcela univerzální. Pokud tradiční swarm routing slouží jako ideální prozatimní ukázka, náš engine je navržen obsloužit libovolný problém, kde se dynamický tok setkává s odporem prostředí.",
                hardware: {
                    title: "Návrh hardwaru a PCB",
                    desc: "Generování organických vodičů odolných vůči rušení. Lineum obchází pravoúhlé zlomy působící jako nežádoucí antény.",
                    link: "Detailní informace →"
                },
                antennas: {
                    title: "Generativní fraktální antény",
                    desc: "Interference vlnoploch zcela přirozeně a efektivně optimalizuje rozložení zářičů pro specifická frekvenční pásma (RF).",
                    link: "Prozkoumat metamateriály →"
                },
                fluid: {
                    title: "Tlakové kanály a chlazení",
                    desc: "Simulujte ideální odvádění tepla a rozvod kapalin ve strojírenství i letectví čistě formou tlakových map.",
                    link: "Topologický průzkum →"
                },
                btn_download: "Stáhnout kompilátor (Brzy)"
            },
            vision: {
                tag: "ZA HRANICE VON NEUMANNA",
                title: "Skutečný potenciál <br /> prostorových výpočtů",
                p1: "Posledních 70 let neustále nutíme spojitou logiku naší prrírody do diskrétních jedniček a nul. Stavíme obrovské grafové algoritmy, abychom náročně simulovali to, co nám fyzikální svět dokáže nabídnout zcela přirozeně a zdarma.",
                p2: "Návratem ke spojitým matematickým rovnicím a interferenci zcela ustupujeme od architektonického úzkého hrdla von Neumannova konceptu.",
                p3: "Nejedná se pouze o nový routovací algoritmus. Prezentujeme fundamentální stavební kámen post-křemíkové formy inteligence.",
                f1_title: "1. Vše bez nutnosti učení",
                f1_desc: "Jakákoliv logika vystupuje okamžitě a přímo s rozložením překážek. Nahrajte půdorys (masku), získejte logickou abstrakci.",
                f2_title: "2. Nekompromisní soukromí",
                f2_desc: "Výpočetní pole si pamatuje celoplošné tlaky, ne datové pakety specifických individuálních agentů.",
                f3_title: "3. Extrémní paralelizace řešení",
                f3_desc: "Vyhodnotí simulaci pro 1 unikátního agenta i pro milion cílů s naprosto totožnou časovou komplexitou – rigorózní algoritmus O(1)."
            },
            calculator: {
                title: "Návratnost serverové latence",
                desc: "Porovnejte, o kolik procent zredukujete zátěž hardwarové infrastruktury výměnou grafových tras (A*) za dynamiku polí.",
                fleet_label: "Aktivní pohybliví agenti",
                ops_label: "API požadavky celkem / den",
                compute_density: "Výpočetní zátěž v uzlech (Density)",
                compute_1: "O(1) masivní tenzorová operace",
                compute_2: "O(N log N) kritické prohledávání",
                compute_3: "Exponenciální míra selkání map"
            },
            cta: {
                title: "Jste připraveni uvolnit blokády?",
                desc: "Implementujte robustní rozhraní Lineum a provždy se vyhněte algoritmickým omezením ve svých systémech.",
                sales: "Kontaktovat Enterprise tým",
                docs: "Analýza a dokumentace (Docs)"
            },
            scenarios: {
                urban: {
                    title: "Městská doprava a logistika",
                    subtitle: "Synchronizace tras desetitisíců cílů současně.",
                    description: "Diskrétní a grafové systémy pravidelně při extrémní datové zátěži kolabují. Ekosystém Lineum vyřeší infrastrukturu velkoměsta na úrovni mikrosekund díky jediné paralelní operaci na matici.",
                    problem: "Grafové hledání z bodu do bodu nesplňuje moderní parametry rychlosti škálování. Jakákoliv dopravní překážka dokáže ochromit a restartovat veškeré operace celého uzlu.",
                    solution: "Globální mapa generující O(1) komplexitu. Jakýkoliv doručovací agent okamžitě a bez přepočítávání intuitivně objíždí formující se shluky zácp přímo 'strháván proudem' odporu."
                },
                evac: {
                    title: "Bezpečnost mas a evakuace",
                    subtitle: "Prevence klenutí a predikce kritického shluku lidských těl.",
                    description: "Dynamické modelování obrovských vln lidí naráz upadajících do paniky. Navrhněte odvětrané dýchající architektury na míru odvrácení těch nejtěžších pošlapání.",
                    problem: "Standardní graf nemůže simulovat fyzický tlak a zachytávání lidských ramen v zúžených koridorech. Tyto 'klenbové' formace tvoří letální smrtící překážky, které jsou před stavbou budovy vizuálně skryté.",
                    solution: "Kapalinová forma tlaku částice přirozeně brání proti překryvům kompresními a radiálními impulsy. Není potřeba žádné složité umělé chování davu – nebezpečí jednoduše plyne přímo ze samotných rovnic jako v řece plné kmenů stromů."
                },
                hardware: {
                    title: "Automatizované PCB spojování",
                    subtitle: "Obvody navržené plynulým odporem bez přehřívání.",
                    description: "Nová éra softwarového návrhu desek plošných spojů. Cestičky křemíkem vznikají samovolným odpuzováním a tvoří organické sítě minimalizující tepelnou stopu pamětí i procesorů.",
                    problem: "Labyrintové přístupy (Lee Algo) generují drtivé pravoúhlé ohyby a hrany, které na obvodech s vysokými frekvencemi působí jako nepatřičné rádiové antény ničící signál.",
                    solution: "Pole se chová jako kapalinový proud protékající mezi komponentami. Linie se přirozeně navzájem míjejí a elegantně optimalizují ty nejkratší plynulé zatáčky, zamezující přeslechům."
                },
                rng: {
                    title: "Entropie z okraje chaosu",
                    subtitle: "Extrakce fraktální termodynamiky pro kryptografii.",
                    description: "Lineum rovnice dokáže uchopit i sebemenší mikro-inženýnské teplotní výchylky CPU hardwaru a skrze iterativní rovnici tento malý lokální šum zvětšit a zesílit ho na obrovskou celoplošnou turbulenci sloužící jako absolutní a neopakovatelný šifrovací klíč nebo Hash.",
                    problem: "Všechny implementace běžných pseudo-náhodných sekvencí (PRNG) nakonec sleví a zacyklí se, dokud nevytvoří prolomitelný bezpečnostní vzorec zranitelnosti.",
                    solution: "Udržujeme vlnový tenzor vždy těsně na hraně teoretického kolapsu (Edge-of-Chaos). Tento stav se nedá oklamat na druhý pokus. Generuje dokonale nelineární laviny na celý operační systém."
                }
            },
            slug: {
                back: "Zpět na API Solutions",
                demo_title: "Modulární test prostředí",
                fail_title: "Reálné selhání grafových algoritmů (A*)",
                success_title: "Aplikovaná fyzikální dynamika polí v čase",
                integration: "Programmatická Integrace a Tenzory"
            }
        }
    },
    en: {
        meta: {
            title: "Lineum | Discrete Field Dynamics",
            description: "A continuous spatial physics engine generating intelligence and logic from emergent wave fields."
        },
        common: {
            brand: "Lineum",
            beta: "BETA"
        },
        nav: {
            portal: "Portal",
            lab: "Laboratory",
            api: "API Solutions",
            wiki: "Wiki / Science",
            support: "Support",
            about: "About Us"
        },
        hero: {
            headline: "Discover the structure of space itself.",
            subheadline: "Hardware without transistors. Computation that doesn't calculate, but grows with the universe.",
            cta_api: "ENTER API",
            cta_lab: "SIMULACRUM & LAB",
            symbol: "Λ",
            title_prefix: "Science of fields that ",
            title_highlight: "breathe.",
            subtitle: "Lineum is an exploration of continuous spatial computation. We study how simple deterministic physics can give rise to emergent, intelligent-looking behavior.",
            cta_wiki: "Explore the Wiki",
            cta_audit: "Audit the Evidence"
        },
        sections: {
            layman: {
                label: "The Philosophy",
                title: "Intelligence from simplicity",
                p1: "Instead of programming explicit rules or training massive neural networks, Lineum asks a different question: What if computation could emerge naturally from the physics of a continuous space?",
                p2: "By designing a specific mathematical environment (Eq-4), we observe the spontaneous formation of stable, particle-like structures that naturally seek optimal paths through their surroundings.",
                visual_label: "Core Interaction"
            },
            scientist: {
                label: "For Researchers",
                title: "Rigorous Verification",
                whitepaper: {
                    title: "The Core Paper",
                    desc: "Read the foundational document defining Eq-4, structural parameters, and the emergent quasiparticle dynamics.",
                    link: "Read the Whitepaper →"
                },
                zenodo: {
                    title: "Open Data Archive",
                    desc: "Access our canonical runs, snapshot metadata, and mathematical proofs in the Zenodo repository.",
                    link: "Go to Zenodo →"
                },
                simulacrum: {
                    title: "Interactive Simulacrum",
                    desc: "A live WebGL environment to test parameter stability and observe field interactions directly in your browser.",
                    link: "Launch Simulacrum →"
                },
                referencePack: {
                    title: "Reference implementation",
                    desc: "Download the source code and reproduction scripts to independently verify our claims on your own hardware.",
                    link: "View on GitHub →"
                }
            }
        },
        legend: {
            trigger_label: "Field Mechanics",
            title: "Simulation Telemetry",
            subtitle: "Live structural observables",
            items: {
                psi: {
                    label: "ψ Phase (Quasiparticles)",
                    description: "The primary entities of the grid. These self-organizing lumps of energy behave like particles, navigating the space according to clear deterministic rules."
                },
                kappa: {
                    label: "κ Environment (Substrate)",
                    description: "The static terrain. These are the fixed boundaries and high-friction zones that shape the movement of particles across the grid."
                },
                phi: {
                    label: "φ Memory (Tension)",
                    description: "The structural memory. As particles move, they leave a temporary physical 'footprint' that repels others from following the exact same path."
                },
                warp: {
                    label: "Topological Warp (Guidance)",
                    description: "The dynamic curvature of the field. This indicates the steepest descent toward optimal destinations, guiding particles like a gravitational pull."
                }
            },
            invitation: "Lineum is fully deterministic. What looks like 'decisions' is just a descent down a self-generated gradient.",
            faq: [
                {
                    q: "Is this an AI neural network?",
                    a: "No. Lineum uses continuous wave equations (Eq-4), not discrete weights or training data. The 'intelligence' emerges naturally from the physics of the field interacting with obstacles."
                },
                {
                    q: "What is a 'linon'?",
                    a: "A linon is a localized clump of wave energy that holds its shape as it moves. Think of them like digital droplets navigating a microscopic landscape to find their target."
                },
                {
                    q: "Why does this matter?",
                    a: "By understanding how nature solves spatial problems through fluid dynamics, we can build fundamentally new approaches to routing, logistics, and simulation."
                }
            ]
        },
        footer: {
            copy: "© 2026 Lineum Project. Released for scientific and research purposes.",
            support: "Support the project (Revolut)",
            github: "GitHub",
            privacy: "Privacy Policy"
        },
        lina: {
            clear_history: "Clear History",
            clear_history_title: "Clear Neural History?",
            confirm_delete: "Confirm Delete",
            cancel: "Cancel",
            clear_history_body: "This will erase all current context and memory.",
            welcome_title: "Research Link Established",
            welcome_body: "I can scan the current whitepapers and simulation logic for you. How can I assist with your research today?",
            show_previous: "Show Previous Context",
            hidden: "hidden",
            recharging: "Recharging",
            auto_retry: "Auto-Retry",
            retry_now: "Retry Now",
            placeholder: "Ask Lina a question...",
            stop_audio: "Stop Audio",
            status_idle: "Click to ask me anything about Lineum ✨",
            status_active: "LINK ESTABLISHED",
            privacy: "Lina is a research instrument. Anonymous conversations may be logged for analysis.",
            insight_header: "EXPLORER INSIGHT"
        },
        wiki: {
            hints: {
                vortex: "✨ Lina: Think of Linons like bubbles in water—always moving but keeping their shape. They are the 'atoms' of our simulation.",
                psi: "✨ Lina: Psi is the main 'actor' here. It tells us where the action is happening at any given moment.",
                kappa: "✨ Lina: Kappa is our tuning map. It's like the terrain that determines how fast a river flows in different places.",
                faq_physics: "✨ Lina: While it looks like physics, Lineum is more like a digital art piece governed by math. We use physics names because they fit the 'vibe'!"
            }
        },
        support: {
            title: "Support the Lineum Project",
            subtitle: "Pushing the boundaries of discrete field dynamics through open research.",
            description: "Lineum is an independent research project dedicated to discovering the fundamental rules of emergent stable excitations. Your support helps cover the computational costs of long-running simulations, maintain our open-source infrastructure, and provide more time for deep scientific analysis.",
            goals: {
                infrastructure: {
                    title: "Computational Infrastructure",
                    desc: "Funding high-uptime servers for audit runs and long-term simulation archiving."
                },
                opensource: {
                    title: "Open Source Development",
                    desc: "Supporting the development of tools like Simulacrum and the Lineum engine."
                },
                research: {
                    title: "Independent Research",
                    desc: "Ensuring that this work remains open, auditable, and free from external constraints."
                }
            },
            cta_label: "Contribute via Revolut"
        },
        whitepaper_warning: {
            title: "Live Research / Documentation Gap",
            paragraphs: [
                "Please note that <b>Lineum is an evolving research project</b>. The static whitepapers here may lag behind the latest audit data and ongoing experiments.",
                "For the most up-to-date understanding, we highly recommend <a href='/api-solutions' style='color: var(--accent-color); text-decoration: underline;'>viewing our Swarm Routing Showcase</a>. It serves as the live proof of our claims, allowing you to observe the continuous field dynamics and emergent particles with your own eyes.",
                "Alternatively, you can <b>ask Lina</b> (the AI Assistant). She has access to the latest live context, audit results, and reformulated hypotheses that might not yet be fully reflected in these texts.",
                "Use these documents as a foundational reference, but trust the live data and Lina for the current state of the art."
            ],
            ack_label: "I Understand, Continue"
        },
        api_solutions: {
            hero: {
                domain: "SPECIALIZED DOMAIN",
                title: "Fluid processing API <br class='hidden sm:block' /> for neuromorphic AI.",
                highlight: "True RNG. Hashing. LPL Logic.",
                subtitle: "Integrate the math of physical wave interference into your B2B stack. Harness Lineum's Edge-of-Chaos dynamics to replace discrete computation with spatial calculation.",
                cta_build: "Start Building",
                cta_docs: "Read Docs"
            },
            roi: {
                title: "Neuromorphic AI Ecosystem",
                subtitle: "Lineum introduces a revolutionary non-von-Neumann architecture. By calculating data physically via fluid wave interference, we unlock <strong class='text-white font-semibold'>True Randomness, Hashing, and LPL Compilers</strong> directly from wave phenomena. No neural network training required."
            },
            features: {
                rng: {
                    title: "True RNG Harvest",
                    desc: "Generates mathematically perfect randomness by amplifying CPU hardware thermal noise at the Edge of Chaos."
                },
                hash: {
                    title: "Avalanche Effect",
                    desc: "One-way cryptographic spatial hashing. A 1-byte payload change rigorously triggers massive topological macro-fractures."
                },
                lpl: {
                    title: "Visual Logic Gates",
                    desc: "Upload a structural CAD mask. The fluid compiles Universal Logic strictly through physical, training-free wave reflections."
                }
            },
            usecases: {
                lpl: {
                    label: "USE CASE 01",
                    title: "Lineum Polygon<br />Language (LPL)",
                    desc: "Forget training neural networks for millions of hours. With LPL, you simply compile a visual CAD mask. The fluid physics engine naturally calculates Universal Logic Gates (AND, OR, XOR) just through wave interference.",
                    bullet1_title: "Zero-Training Intelligence",
                    bullet1_desc: "Compute logic visually via physical geometry.",
                    bullet2_title: "Geometric Telemetry",
                    bullet2_desc: "Receive raw mathematical standing wave interference as JSON output."
                },
                rng: {
                    label: "USE CASE 02",
                    title: "True RNG &<br />Cryptographic Hashing",
                    desc: "By running the fluid equation at the mathematical \"Edge of Chaos\", Lineum amplifies microscopic CPU thermal float variance into massive waves. This generates mathematically perfect True Random Numbers and One-Way Avalanche Hashing.",
                    bullet1_title: "Hardware Entropy Harvest",
                    bullet1_desc: "Does not rely on pseudo-RNG formulas. Harvests physical CPU timing errors.",
                    bullet2_title: "Extreme Avalanche Effect",
                    bullet2_desc: "A 1-byte payload difference causes a rigorous topological macro-fracture."
                }
            },
            demos: {
                title: "Live Interactive Prototypes",
                desc: "Experiment with the Lineum Core tensor engine directly in your browser."
            },
            domains: {
                title: "Explore Specialized Domains",
                desc: "The Lineum equation is terrain-agnostic. While swarm routing is our most visible application, the engine natively handles any scenario where continuous flow meets resistance.",
                hardware: {
                    title: "PCB & Hardware Routing",
                    desc: "Generate organic, interference-free curve traces for printed circuit boards and silicon. Avoid 90° corners that act as antennas.",
                    link: "Explore Technical Details →"
                },
                antennas: {
                    title: "Generative Antennas",
                    desc: "The wavefront interference naturally finds resonant fractal geometries for RF antennas, optimizing for specific frequency bands automatically.",
                    link: "Explore Metamaterials →"
                },
                fluid: {
                    title: "Fluid & Heat Topologies",
                    desc: "Calculate optimal cooling channel designs for aerospace and automotive parts using pure pressure gradients.",
                    link: "Explore Topology →"
                },
                btn_download: "Download SDK (Coming Soon)"
            },
            vision: {
                tag: "BEYOND VON NEUMANN",
                title: "The True Potential of <br /> Spatial Computation",
                p1: "For 70 years, we've forced nature's continuous logic into discrete 1s and 0s. We've built towering algorithms to simulate what the physical world calculates for free.",
                p2: "By returning to continuous physics via the Lineum equation, we bypass the von Neumann bottleneck entirely.",
                p3: "This isn't just a new routing algorithm. It's the blueprint for post-silicon intelligence.",
                f1_title: "1. No Training Required",
                f1_desc: "Logic emerges directly from geometry. Upload a CAD mask, get intelligence.",
                f2_title: "2. Absolute Privacy",
                f2_desc: "The field remembers pressure, not individual agent identities or payloads.",
                f3_title: "3. Infinite Parallelism",
                f3_desc: "Resolves 1 or 1,000,000 agents in the exact same O(1) time complexity."
            },
            calculator: {
                title: "Latency & Compute ROI",
                desc: "See how replacing A* with Lineum Field Dynamics saves infrastructure costs.",
                fleet_label: "Active Agents / Fleet",
                ops_label: "API Calls / Day",
                compute_density: "Compute Density",
                compute_1: "O(1) tensor op",
                compute_2: "O(N log N) graph search",
                compute_3: "Exponential graph failure"
            },
            cta: {
                title: "Ready to scale your domain?",
                desc: "Deploy Lineum API and eliminate algorithmic bottlenecks today.",
                sales: "Contact Enterprise Sales",
                docs: "Read Documentation"
            },
            scenarios: {
                urban: {
                    title: 'Urban Traffic & Logistics',
                    subtitle: 'Routing 10,000 agents without graph algorithms.',
                    description: 'Traditional discrete routing (A*) collapses when calculating dynamic traffic for thousands of agents simultaneously. The Lineum Field processes entire cities in a single tensor operation.',
                    problem: 'Graph algorithms scale poorly (O(N*logN)) for multiple agents. In dense urban grids, updating traffic values triggers cascading recalculations across the entire network.',
                    solution: 'Lineum computes the resistance landscape globally in O(1). All agents simply flow down the gradient, reacting to congestion instantly without pathfinding overhead.',
                },
                evac: {
                    title: 'Crowd Panic & Evacuation',
                    subtitle: 'Real-time bottleneck prevention in stadiums.',
                    description: 'Model massive crowd dynamics. Understand how physical constraints and panic behaviors lead to dangerous arching and crushing, and design exits that breathe.',
                    problem: 'Evacuation modeling requires fluid-like equations combined with discrete agent goals. Standard shortest-path algorithms ignore the physical space agents take up, failing to predict lethal crushes.',
                    solution: 'The Lineum spatial field models agents as repulsive density waves. Bottlenecks naturally emerge from the math, allowing architects to optimize hallways long before concrete is poured.',
                },
                hardware: {
                    title: 'Hardware & Dielectric Routing',
                    subtitle: 'Finding optimal tracks on multi-layer PCBs.',
                    description: 'Autorouting for complex printed circuit boards (PCBs) or VLSI chips. Lineum naturally finds non-intersecting, optimal trace paths around thousands of components.',
                    problem: 'Traditional PCB autorouters use grid-based maze-solving (Lee algorithm), which scales terribly on high-density boards, often failing to find 100% completion.',
                    solution: 'Lineum treats components as impenetrable barriers and traces as flowing rivers of current. The field inherently repels competing traces, finding harmonious layouts organically.',
                },
                rng: {
                    title: 'True RNG & Thermodynamic Entropy',
                    subtitle: 'Harvesting edge-of-chaos physics.',
                    description: 'Leverage the Lineum chaotic fluid equations to magnify microscopic hardware thermal fluctuations into a cryptographically unassailable entropy source.',
                    problem: 'Standard pseudo-RNG algorithms eventually repeat or reveal a pattern. They are deterministic mathematical formulas rather than genuinely unpredictable environmental noise.',
                    solution: 'By pushing the wave calculations directly to the phase-transition threshold (the edge of chaos), we harness pure spatial turbulence, making patterns impossible to predict.',
                }
            },
            slug: {
                back: "Back to API Solutions",
                demo_title: "WebGL Module Provisioning",
                fail_title: "Graph Algorithm Failure (A*)",
                success_title: "Continuous Field Dynamics",
                integration: "Production Integration"
            }
        }
    },
    de: {
        meta: {
            title: "Lineum | Diskrete Felddynamik",
            description: "Eine kontinuierliche räumliche Physik-Engine, die Intelligenz und Logik aus emergenten Wellenfeldern erzeugt."
        },

        common: {
            brand: "Lineum",
            beta: "BETA"
        },
        nav: {
            portal: "Portal",
            lab: "Labor",
            api: "API-Lösungen",
            wiki: "Wiki / Science",
            support: "Support",
            about: "Über uns"
        },
        hero: {
            headline: "Entdecken Sie die Struktur des Raumes.",
            subheadline: "Hardware ohne Transistoren. Berechnungen, die nicht kalkulieren, sondern mit dem Universum wachsen.",
            cta_api: "ZUR API",
            cta_lab: "SIMULACRUM & LABOR",
            symbol: "Λ",
            title_prefix: "Die Wissenschaft von Feldern, die ",
            title_highlight: "atmen.",
            subtitle: "Lineum ist eine Erforschung kontinuierlicher räumlicher Berechnungen. Wir untersuchen, wie einfache deterministische Physik intelligentes Verhalten hervorbringen kann.",
            cta_wiki: "Wiki erkunden",
            cta_audit: "Beweise prüfen"
        },
        sections: {
            layman: {
                label: "Die Philosophie",
                title: "Intelligenz durch Einfachheit",
                p1: "Anstatt explizite Regeln zu programmieren oder riesige neuronale Netze zu trainieren, stellt Lineum eine andere Frage: Was wäre, wenn Berechnungen auf natürliche Weise aus der Physik eines kontinuierlichen Raums entstehen könnten?",
                p2: "Durch die Entwicklung einer spezifischen mathematischen Umgebung (Gleichung Eq-4) beobachten wir die spontane Bildung stabiler, teilchenartiger Strukturen, die auf natürliche Weise optimale Pfade durch ihre Umgebung suchen.",
                visual_label: "Kerninteraktion"
            },
            scientist: {
                label: "Für Forscher",
                title: "Rigorose Verifizierung",
                whitepaper: {
                    title: "Das Kernpapier",
                    desc: "Lesen Sie das grundlegende Dokument, das Eq-4, die strukturellen Parameter und die Dynamik von Quasiteilchen definiert.",
                    link: "Whitepaper lesen →"
                },
                zenodo: {
                    title: "Offenes Datenarchiv",
                    desc: "Greifen Sie auf unsere kanonischen Läufe, Metadaten und mathematischen Beweise im Zenodo-Repository zu.",
                    link: "Zu Zenodo →"
                },
                simulacrum: {
                    title: "Interaktives Simulacrum",
                    desc: "Eine Live-WebGL-Umgebung, um Parameterstabilität zu testen und Feldinteraktionen direkt in Ihrem Browser zu beobachten.",
                    link: "Simulacrum starten →"
                },
                referencePack: {
                    title: "Referenzimplementierung",
                    desc: "Laden Sie den Quellcode und die Reproduktionsskripte herunter, um unsere Behauptungen auf Ihrer eigenen Hardware unabhängig zu überprüfen.",
                    link: "Auf GitHub ansehen →"
                }
            }
        },
        legend: {
            trigger_label: "Feldmechanik",
            title: "Simulations-Telemetrie",
            subtitle: "Live-Strukturvariablen",
            items: {
                psi: {
                    label: "ψ Phase (Quasiteilchen)",
                    description: "Die Hauptentitäten des Rasters. Diese sich selbst organisierenden Energieklumpen verhalten sich wie Teilchen und navigieren nach klaren deterministischen Regeln durch den Raum."
                },
                kappa: {
                    label: "κ Umgebung (Substrat)",
                    description: "Das statische Terrain. Dies sind die festen Grenzen und Hochreibungszonen, die die Bewegung von Teilchen über das Raster formen."
                },
                phi: {
                    label: "φ Gedächtnis (Spannung)",
                    description: "Das strukturelle Gedächtnis. Wenn sich Teilchen bewegen, hinterlassen sie einen temporären physischen 'Fußabdruck', der andere davon abhält, genau demselben Pfad zu folgen."
                },
                warp: {
                    label: "Topologischer Warp (Führung)",
                    description: "Die dynamische Krümmung des Feldes. Sie zeigt das steilste Gefälle zu optimalen Zielen an und lenkt Teilchen wie eine Anziehungskraft."
                }
            },
            invitation: "Lineum ist vollständig deterministisch. Was wie 'Entscheidungen' aussieht, ist nur ein Abstieg entlang eines selbst generierten Gradienten.",
            faq: [
                {
                    q: "Ist das ein KI-Neuronales-Netz?",
                    a: "Nein. Lineum verwendet kontinuierliche Wellengleichungen (Eq-4), keine diskreten Gewichtungen oder Trainingsdaten. Die 'Intelligenz' entsteht natürlich aus der Physik des Feldes bei Interaktion mit Hindernissen."
                },
                {
                    q: "Was ist ein 'Linon'?",
                    a: "Ein Linon ist ein lokalisiertes Klümpchen Wellenenergie, das seine Form beibehält, während es sich bewegt. Stellen Sie sich digitale Tropfen vor, die durch eine mikroskopische Landschaft navigieren, um ihr Ziel zu finden."
                },
                {
                    q: "Warum ist das wichtig?",
                    a: "Indem wir verstehen, wie die Natur räumliche Probleme durch Fluiddynamik löst, können wir grundlegend neue Ansätze für Routing, Logistik und Simulationen entwickeln."
                }
            ]
        },
        footer: {
            copy: "© 2026 Lineum-Projekt. Veröffentlicht für wissenschaftliche und Forschungszwecke.",
            support: "Projekt unterstützen (Revolut)",
            github: "GitHub",
            privacy: "Datenschutzerklärung"
        },
        lina: {
            clear_history: "Verlauf löschen",
            clear_history_title: "Neuronale Verbindung trennen?",
            confirm_delete: "Löschen bestätigen",
            cancel: "Abbrechen",
            clear_history_body: "Dadurch werden alle aktuellen Kontexte und Erinnerungen gelöscht.",
            welcome_title: "Forschungsverbindung hergestellt",
            welcome_body: "Ich kann die aktuellen Whitepapers und die Simulationslogik für Sie scannen. Wie kann ich heute bei Ihrer Forschung helfen?",
            show_previous: "Vorherigen Kontext anzeigen",
            hidden: "versteckt",
            recharging: "Ladevorgang",
            auto_retry: "Auto-Retry",
            retry_now: "Erneut versuchen",
            placeholder: "Stellen Sie Lina eine Frage...",
            stop_audio: "Audio stoppen",
            status_idle: "Frag mich nach Lineum ✨",
            status_active: "VERBINDUNG HERGESTELLT",
            privacy: "Lina ist ein Forschungsinstrument. Anonyme Gespräche können zu Analysezwecken gespeichert werden.",
            insight_header: "ENTDECKER-EINBLICK"
        },
        wiki: {
            hints: {
                vortex: "✨ Lina: Stellen Sie sich Linons wie Blasen im Wasser vor – sie bewegen sich ständig, behalten aber ihre Form. Sie sind die 'Atome' unserer Simulation.",
                psi: "✨ Lina: Psi ist hier der Hauptakteur. Es sagt uns, wo die Action zu einem bestimmten Zeitpunkt stattfindet.",
                kappa: "✨ Lina: Kappa ist unsere Abstimmkarte. Es ist wie das Gelände, das bestimmt, wie schnell ein Fluss an verschiedenen Orten fließt.",
                faq_physics: "✨ Lina: Obwohl es wie Physik aussieht, ist Lineum eher ein von Mathematik gesteuertes digitales Kunstwerk. Wir verwenden physikalische Namen, weil sie zur 'Stimmung' passen!"
            }
        },
        support: {
            title: "Unterstützen Sie das Lineum-Projekt",
            subtitle: "Die Grenzen diskreter Felddynamik durch offene Forschung verschieben.",
            description: "Lineum ist ein unabhängiges Forschungsprojekt zur Entdeckung der grundlegenden Regeln emergenter stabiler Anregungen. Ihre Unterstützung hilft, die Rechenkosten zu decken, unsere Open-Source-Infrastruktur aufrechtzuerhalten und mehr Zeit für tiefe wissenschaftliche Analysen zu schaffen.",
            goals: {
                infrastructure: {
                    title: "Recheninfrastruktur",
                    desc: "Finanzierung hochverfügbarer Server für Audits und Langzeitarchivierung."
                },
                opensource: {
                    title: "Open-Source-Entwicklung",
                    desc: "Unterstützung bei der Entwicklung von Tools wie dem Simulacrum und der Lineum-Engine."
                },
                research: {
                    title: "Unabhängige Forschung",
                    desc: "Sicherstellen, dass diese Arbeit offen, überprüfbar und frei von externen Zwängen bleibt."
                }
            },
            cta_label: "Via Revolut beitragen"
        },
        whitepaper_warning: {
            title: "Live-Forschung / Dokumentationslücke",
            paragraphs: [
                "Bitte beachten Sie, dass <b>Lineum ein sich entwickelndes Forschungsprojekt ist</b>. Die statischen Whitepapers hier können hinter aktuellen Audits und Experimenten zurückbleiben.",
                "Für das aktuellste Verständnis empfehlen wir dringend, <a href='/api-solutions' style='color: var(--accent-color); text-decoration: underline;'>unseren Swarm Routing Showcase anzusehen</a>. Es dient als Live-Beweis unserer Behauptungen.",
                "Alternativ können Sie <b>Lina fragen</b> (die KI-Assistentin). Sie hat Zugriff auf den neuesten Kontext, Auditergebnisse und umformulierte Hypothesen.",
                "Nutzen Sie diese Dokumente als Grundlage, aber vertrauen Sie den Live-Daten und Lina für den aktuellen Stand."
            ],
            ack_label: "Ich verstehe, weiter"
        }
    },
    ja: {
        meta: {
            title: "Lineum | 離散場力学",
            description: "創発的な波動場から知能と論理を生成する連続空間物理エンジン。"
        },
        api_solutions: {
            hero: {
                domain: "SPECIALIZED DOMAIN",
                title: "Fluid processing API <br class='hidden sm:block' /> for neuromorphic AI.",
                highlight: "True RNG. Hashing. LPL Logic.",
                subtitle: "Integrate the math of physical wave interference into your B2B stack. Harness Lineum's Edge-of-Chaos dynamics to replace discrete computation with spatial calculation.",
                cta_build: "Start Building",
                cta_docs: "Read Docs"
            },
            roi: {
                title: "Neuromorphic AI Ecosystem",
                subtitle: "Lineum introduces a revolutionary non-von-Neumann architecture. By calculating data physically via fluid wave interference, we unlock <strong class='text-white font-semibold'>True Randomness, Hashing, and LPL Compilers</strong> directly from wave phenomena. No neural network training required."
            },
            features: {
                rng: {
                    title: "True RNG Harvest",
                    desc: "Generates mathematically perfect randomness by amplifying CPU hardware thermal noise at the Edge of Chaos."
                },
                hash: {
                    title: "Avalanche Effect",
                    desc: "One-way cryptographic spatial hashing. A 1-byte payload change rigorously triggers massive topological macro-fractures."
                },
                lpl: {
                    title: "Visual Logic Gates",
                    desc: "Upload a structural CAD mask. The fluid compiles Universal Logic strictly through physical, training-free wave reflections."
                }
            },
            usecases: {
                lpl: {
                    label: "USE CASE 01",
                    title: "Lineum Polygon<br />Language (LPL)",
                    desc: "Forget training neural networks for millions of hours. With LPL, you simply compile a visual CAD mask. The fluid physics engine naturally calculates Universal Logic Gates (AND, OR, XOR) just through wave interference.",
                    bullet1_title: "Zero-Training Intelligence",
                    bullet1_desc: "Compute logic visually via physical geometry.",
                    bullet2_title: "Geometric Telemetry",
                    bullet2_desc: "Receive raw mathematical standing wave interference as JSON output."
                },
                rng: {
                    label: "USE CASE 02",
                    title: "True RNG &<br />Cryptographic Hashing",
                    desc: "By running the fluid equation at the mathematical \"Edge of Chaos\", Lineum amplifies microscopic CPU thermal float variance into massive waves. This generates mathematically perfect True Random Numbers and One-Way Avalanche Hashing.",
                    bullet1_title: "Hardware Entropy Harvest",
                    bullet1_desc: "Does not rely on pseudo-RNG formulas. Harvests physical CPU timing errors.",
                    bullet2_title: "Extreme Avalanche Effect",
                    bullet2_desc: "A 1-byte payload difference causes a rigorous topological macro-fracture."
                }
            },
            demos: {
                title: "Live Interactive Prototypes",
                desc: "Experiment with the Lineum Core tensor engine directly in your browser."
            },
            domains: {
                title: "Explore Specialized Domains",
                desc: "The Lineum equation is terrain-agnostic. While swarm routing is our most visible application, the engine natively handles any scenario where continuous flow meets resistance.",
                hardware: {
                    title: "PCB & Hardware Routing",
                    desc: "Generate organic, interference-free curve traces for printed circuit boards and silicon. Avoid 90° corners that act as antennas.",
                    link: "Explore Technical Details →"
                },
                antennas: {
                    title: "Generative Antennas",
                    desc: "The wavefront interference naturally finds resonant fractal geometries for RF antennas, optimizing for specific frequency bands automatically.",
                    link: "Explore Metamaterials →"
                },
                fluid: {
                    title: "Strömungs- und Wärmetopologien",
                    desc: "Berechnen Sie optimale Kühlkanaldesigns für Luft- und Raumfahrtteile mithilfe reiner Druckgradienten.",
                    link: "Topologie erkunden →"
                },
                btn_download: "SDK Herunterladen (Demnächst)"
            },
            vision: {
                tag: "JENSEITS VON NEUMANN",
                title: "Das wahre Potenzial <br /> Räumlicher Berechnungen",
                p1: "Seit 70 Jahren zwingen wir die kontinuierliche Logik der Natur in diskrete 1en und 0en. Wir bauen riesige Algorithmen, um das zu simulieren, was die physische Welt kostenlos berechnet.",
                p2: "Indem wir zur kontinuierlichen Physik über die Lineum-Gleichung zurückkehren, umgehen wir den von-Neumann-Engpass vollständig.",
                p3: "Dies ist nicht nur ein neuer Routing-Algorithmus. Es ist der Entwurf für Post-Silicon-Intelligenz.",
                f1_title: "1. Kein Training erforderlich",
                f1_desc: "Logik entsteht direkt aus der Geometrie. Laden Sie eine CAD-Maske hoch, erhalten Sie Intelligenz.",
                f2_title: "2. Absolute Privatsphäre",
                f2_desc: "Das Feld speichert Druck, keine individuellen Agentenidentitäten oder Datenpakete.",
                f3_title: "3. Unendliche Parallelität",
                f3_desc: "Löst 1 oder 1.000.000 Agenten in exakt derselben O(1)-Zeitkomplexität auf."
            },
            calculator: {
                title: "Latenz & Compute ROI",
                desc: "Sehen Sie, wie der Ersatz von A* durch Lineum Field Dynamics Infrastrukturkosten spart.",
                fleet_label: "Aktive Agenten",
                ops_label: "API-Aufrufe / Tag",
                compute_density: "Berechnungsdichte",
                compute_1: "O(1) Tensor-Operation",
                compute_2: "O(N log N) Graphensuche",
                compute_3: "Exponentieller Ausfall"
            },
            cta: {
                title: "Ready to scale your domain?",
                desc: "Deploy Lineum API and eliminate algorithmic bottlenecks today.",
                sales: "Contact Enterprise Sales",
                docs: "Read Documentation"
            },
            scenarios: {
                urban: {
                    title: 'Urban Traffic & Logistics',
                    subtitle: 'Routing 10,000 agents without graph algorithms.',
                    description: 'Traditional discrete routing (A*) collapses when calculating dynamic traffic for thousands of agents simultaneously. The Lineum Field processes entire cities in a single tensor operation.',
                    problem: 'Graph algorithms scale poorly (O(N*logN)) for multiple agents. In dense urban grids, updating traffic values triggers cascading recalculations across the entire network.',
                    solution: 'Lineum computes the resistance landscape globally in O(1). All agents simply flow down the gradient, reacting to congestion instantly without pathfinding overhead.',
                },
                evac: {
                    title: 'Crowd Panic & Evacuation',
                    subtitle: 'Real-time bottleneck prevention in stadiums.',
                    description: 'Model massive crowd dynamics. Understand how physical constraints and panic behaviors lead to dangerous arching and crushing, and design exits that breathe.',
                    problem: 'Evacuation modeling requires fluid-like equations combined with discrete agent goals. Standard shortest-path algorithms ignore the physical space agents take up, failing to predict lethal crushes.',
                    solution: 'The Lineum spatial field models agents as repulsive density waves. Bottlenecks naturally emerge from the math, allowing architects to optimize hallways long before concrete is poured.',
                },
                hardware: {
                    title: 'Hardware & Dielectric Routing',
                    subtitle: 'Finding optimal tracks on multi-layer PCBs.',
                    description: 'Autorouting for complex printed circuit boards (PCBs) or VLSI chips. Lineum naturally finds non-intersecting, optimal trace paths around thousands of components.',
                    problem: 'Traditional PCB autorouters use grid-based maze-solving (Lee algorithm), which scales terribly on high-density boards, often failing to find 100% completion.',
                    solution: 'Lineum treats components as impenetrable barriers and traces as flowing rivers of current. The field inherently repels competing traces, finding harmonious layouts organically.',
                },
                rng: {
                    title: 'True RNG & Thermodynamic Entropy',
                    subtitle: 'Harvesting edge-of-chaos physics.',
                    description: 'Leverage the Lineum chaotic fluid equations to magnify microscopic hardware thermal fluctuations into a cryptographically unassailable entropy source.',
                    problem: 'Standard pseudo-RNG algorithms eventually repeat or reveal a pattern. They are deterministic mathematical formulas rather than genuinely unpredictable environmental noise.',
                    solution: 'By pushing the wave calculations directly to the phase-transition threshold (the edge of chaos), we harness pure spatial turbulence, making patterns impossible to predict.',
                }
            },
            slug: {
                back: "Back to API Solutions",
                demo_title: "WebGL Module Provisioning",
                fail_title: "Graph Algorithm Failure (A*)",
                success_title: "Continuous Field Dynamics",
                integration: "Production Integration"
            }
        },
        common: {
            brand: "Lineum",
            beta: "BETA"
        },
        nav: {
            portal: "ポータル",
            lab: "研究所 [Lab]",
            api: "API ソリューション",
            wiki: "Wiki / Science",
            support: "サポート",
            about: "私たちについて"
        },
        hero: {
            headline: "空間そのものの構造を発見する。",
            subheadline: "トランジスタのないハードウェア。計算ではなく、宇宙とともに成長する演算。",
            cta_api: "APIに入る",
            cta_lab: "シミュラクラムと研究所",
            symbol: "Λ",
            title_prefix: "呼吸する場の",
            title_highlight: "科学。",
            subtitle: "Lineumは連続的な空間計算の探求です。単純な決定論的物理学が、どのように創発的で知的な振る舞いを生み出すかを研究しています。",
            cta_wiki: "Wikiを探索",
            cta_audit: "エビデンスの監査"
        },
        sections: {
            layman: {
                label: "哲学",
                title: "単純さから生まれる知能",
                p1: "明示的なルールをプログラミングしたり、巨大なニューラルネットワークを学習させる代わりに、Lineumは別の問いを立てます：もし計算が連続空間の物理学から自然に生じるとしたらどうでしょうか？",
                p2: "特定の数学的環境（Eq-4）を設計することで、安定した粒子状の構造体が自発的に形成され、周囲の環境を通して自然に最適な経路を探し出す様子を観察できます。",
                visual_label: "コア相互作用"
            },
            scientist: {
                label: "研究者向け",
                title: "厳密な検証",
                whitepaper: {
                    title: "コアペーパー",
                    desc: "Eq-4、構造パラメータ、創発的な準粒子ダイナミクスを定義する基礎文書をお読みください。",
                    link: "ホワイトペーパーを読む →"
                },
                zenodo: {
                    title: "オープンデータアーカイブ",
                    desc: "Zenodoリポジトリで、カノニカル実行、メタデータ、および数学的証明にアクセスできます。",
                    link: "Zenodoへ →"
                },
                simulacrum: {
                    title: "インタラクティブ・シミュラクラム",
                    desc: "ブラウザ上でパラメータの安定性をテストし、フィールドの相互作用を直接観察できるLive WebGL環境です。",
                    link: "シミュラクラムを起動 →"
                },
                referencePack: {
                    title: "リファレンス実装",
                    desc: "ソースコードと再現スクリプトをダウンロードして、ご自身のハードウェアで我々の主張を独立して検証できます。",
                    link: "GitHubで見る →"
                }
            }
        },
        legend: {
            trigger_label: "フィールド力学",
            title: "シミュレーション・テレメトリー",
            subtitle: "ライブ構造の観測量",
            items: {
                psi: {
                    label: "ψ 位相 (準粒子)",
                    description: "グリッドの主要なエンティティ。これらの自己組織化するエネルギーの塊は粒子のように振る舞い、明確な決定論的ルールに従って空間を移動します。"
                },
                kappa: {
                    label: "κ 環境 (基質)",
                    description: "静的な地形。これらは、グリッド上の粒子の動きを形成する固定された境界と高摩擦ゾーンです。"
                },
                phi: {
                    label: "φ 記憶 (張力)",
                    description: "構造的な記憶。粒子が移動すると、他の粒子が全く同じ経路をたどるのを反発する一時的な物理的「足跡」を残します。"
                },
                warp: {
                    label: "トポロジカル・ワープ (誘導)",
                    description: "空間の動的な曲率。これは最適な目的地への最も急な降下を示し、重力のように粒子を導きます。"
                }
            },
            invitation: "Lineumは完全に決定論的です。「意思決定」のように見えるものは、自己生成された勾配を下る現象にすぎません。",
            faq: [
                {
                    q: "これはAIニューラルネットワークですか？",
                    a: "いいえ。Lineumは、離散的な重みや学習データではなく、連続波動方程式（Eq-4）を使用します。「知能」は、場と障害物との相互作用の物理学から自然に生じます。"
                },
                {
                    q: "「ライノン（linon）」とは何ですか？",
                    a: "ライノンは、移動しながらその形状を保つ波エネルギーの局所的な塊です。ターゲットを見つけるために微視的な風景をナビゲートするデジタルの雫と考えてください。"
                },
                {
                    q: "なぜこれが重要なのであるか？",
                    a: "自然が流体力学を介して空間問題をどのように解決するかを理解することで、ルーティング、ロジスティクス、シミュレーションへの全く新しいアプローチを構築できます。"
                }
            ]
        },
        footer: {
            copy: "© 2026 Lineumプロジェクト。科学および研究目的のために公開されています。",
            support: "プロジェクトの支援 (Revolut)",
            github: "GitHub",
            privacy: "プライバシーポリシー"
        },
        lina: {
            clear_history: "履歴をクリア",
            clear_history_title: "神経履歴をクリアしますか？",
            confirm_delete: "削除の確認",
            cancel: "キャンセル",
            clear_history_body: "現在のすべてのコンテキストとメモリが消去されます。",
            welcome_title: "研究リンクが確立されました",
            welcome_body: "現在のホワイトペーパーとシミュレーションロジックをスキャンできます。本日の研究をどのように支援できますか？",
            show_previous: "以前の文脈を表示",
            hidden: "隠し",
            recharging: "充電中",
            auto_retry: "自動再試行",
            retry_now: "今すぐ再試行",
            placeholder: "Linaに質問する...",
            stop_audio: "音声を停止",
            status_idle: "クリックしてLineumについて質問してください ✨",
            status_active: "リンク確立",
            privacy: "リナは研究ツールです。匿名の会話は分析のために保存される場合があります。",
            insight_header: "エクスプローラーの洞察"
        },
        wiki: {
            hints: {
                vortex: "✨ リナ：ライノンは水中の泡のようなものだと考えてください。常に動いていますが、形は保たれています。これらは私たちのシミュレーションの「原子」です。",
                psi: "✨ リナ：ここではプサイが「主役」です。特定の瞬間にどこでアクションが起こっているかを教えてくれます。",
                kappa: "✨ リナ：カッパは私たちのチューニングマップです。場所によって川の流れる速さを決める地形のようなものです。",
                faq_physics: "✨ リナ：物理学のように見えますが、Lineumは数学によって支配されるデジタルアート作品のようなものです。「雰囲気」に合うので物理学の名前を使っています！"
            }
        },
        support: {
            title: "Lineumプロジェクトの支援",
            subtitle: "オープンな研究を通じて離散場力学の限界を押し広げる。",
            description: "Lineumは、創発的で安定した励起の基本法則を発見することに専念する独立した研究プロジェクトです。皆様の支援は、長時間実行されるシミュレーションの計算コストをカバーし、オープンソースインフラストラクチャを維持し、深い科学的分析のためのより多くの時間を提供するのに役立ちます。",
            goals: {
                infrastructure: {
                    title: "計算インフラストラクチャ",
                    desc: "監査の実行と長期的なシミュレーションのアーカイブ化のための稼働率の高いサーバーの資金調達。"
                },
                opensource: {
                    title: "オープンソース開発",
                    desc: "シミュラクラムやLineumエンジンなどのツールの開発のサポート。"
                },
                research: {
                    title: "独立した研究",
                    desc: "この作業がオープンで、監査可能であり、外部の制約から自由であることを保証する。"
                }
            },
            cta_label: "Revolut経由で貢献"
        },
        whitepaper_warning: {
            title: "ライブ研究 / ドキュメントのギャップ",
            paragraphs: [
                "<b>Lineumは進化する研究プロジェクトです</b>。ここにある静的なホワイトペーパーは、最新の監査データや進行中の実験に遅れをとる可能性があります。",
                "最新の理解のために、<a href='/api-solutions' style='color: var(--accent-color); text-decoration: underline;'>Swarm Routing Showcase</a>をご覧になることを強くお勧めします。これは私たちの主張のライブ証拠として機能します。",
                "または、<b>Lina（AIアシスタント）に質問</b>することもできます。彼女は、最新のライブコンテキスト、監査結果、および再構成された仮説にアクセスできます。",
                "これらのドキュメントを基礎的なリファレンスとして使用しつつも、現状についてはライブデータとLinaを信頼してください。"
            ],
            ack_label: "理解しました、続行します"
        }
    }
};

// Auto-detection logic (browser language)
const getInitialLang = () => {
    if (typeof window !== 'undefined') {
        // 1. Explicit user preference overrides everything
        const saved = window.localStorage.getItem('portal_lang');
        if (saved) return saved;

        // 2. Fallback to browser language
        const navLang = window.navigator.language.toLowerCase();
        if (navLang.startsWith('cs') || navLang.startsWith('sk')) {
            return 'cs';
        }
        if (navLang.startsWith('de')) return 'de';
        if (navLang.startsWith('ja')) return 'ja';
    }
    return 'en'; // 3. Global default fallback
};

export const locale = writable(getInitialLang());

// Subscribe to locale changes to persist in localStorage if in browser
if (typeof window !== 'undefined' && window.localStorage) {
    locale.subscribe(val => {
        window.localStorage.setItem('portal_lang', val);
    });
}

// Helper to resolve dot.notation.paths
export function resolveKey(obj: any, path: string): string | undefined {
    if (!path || typeof path !== 'string') return undefined;

    // Arrays handle bracket notation by default here manually since it's just keys like faq.0.q
    return path.split('.').reduce((prev, curr) => {
        return prev ? prev[curr] : undefined;
    }, obj);
}

// The main translation store function `$t('namespace.key')`
export const t = derived(locale, ($locale) => (key: string) => {
    // Ensure TypeScript knows key paths exist on translations
    const typedTranslations = translations as any;

    let res = resolveKey(typedTranslations[$locale], key);

    // Fallback to English if Czech is missing
    if (res === undefined && $locale !== 'en') {
        res = resolveKey(typedTranslations['en'], key);
    }

    // Absolute fallback - Loud warning
    if (res === undefined) {
        return `[MISSING: ${key}]`;
    }

    return res as string | any; // Could return an object if parent key is queried, components must handle it
});
