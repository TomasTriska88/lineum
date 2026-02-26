import fs from 'fs';

/**
 * ============================================================================
 * LINA EASTER EGGS - CONTENT GUIDELINES & MANIFESTO
 * ============================================================================
 * 
 * IMPORTANT FOR FUTURE MAINTAINERS:
 * When adding or modifying these Easter eggs, strictly adhere to the following rules:
 * 
 * 1. GREEN-LIGHT TONE ONLY:
 *    The messages MUST sound like the system is functioning perfectly and is 
 *    ready for action ("All systems nominal", "Shields up", "Ready for input").
 * 
 * 2. NO ERROR/MALWARE SCARE TACTICS:
 *    NEVER use words like "deadlock", "malware", "virus", "error", "vulnerability",
 *    or phrases that imply the AI is disobeying ("I can't do that, Dave"). 
 *    This is a corporate landing page and we must not confuse or scare users 
 *    into thinking the website is actually broken or under attack.
 * 
 * 3. NO TRAILING PERIODS:
 *    Do NOT put periods (.) or Japanese periods (。) at the end of the strings. 
 *    The UI automatically appends a blinking terminal cursor directly after the 
 *    last character, and trailing periods break the illusion. Question marks (?) 
 *    and exclamation marks (!) are acceptable and can be kept.
 * 
 * 4. KEEP IT SUBTLE YET GEEKY:
 *    Sci-fi, cyber, and pop-culture references are highly encouraged, as long 
 *    as they fit the "ready and waiting" system persona.
 * 
 * 5. NO UNCERTAINTY OR HESITATION:
 *    The AI should never sound doubtful about its capabilities. Avoid phrases
 *    like "I'll try", "I hope", "I can't promise", etc.
 *    Always use confident, absolute statements like "Commencing calculation".
 * ============================================================================
 */

const eggsObj = {
    // General Sci-fi / Operations
    "lina_egg_1": {
        "en": "Conditions optimal for data retrieval.",
        "cs": "Podmínky pro zisk dat jsou optimální.",
        "de": "Bedingungen für Datenabruf optimal.",
        "ja": "データ検索に最適な条件。"
    },
    // Sci-fi trope (Stabilizing the flow)
    "lina_egg_2": {
        "en": "I can stabilize the flow for a brief window.",
        "cs": "Mohu stabilizovat tok na krátký okamžik.",
        "de": "Ich kann den Fluss kurz stabilisieren.",
        "ja": "流れを一時的に安定させることができます。"
    },
    // General fantasy/RPG trope
    "lina_egg_3": {
        "en": "Greetings, Traveler. The gateway is open.",
        "cs": "Zdravím, Cestovateli. Brána je otevřena.",
        "de": "Sei gegrüßt, Reisender. Das Tor ist offen.",
        "ja": "ようこそ、旅人よ。ゲートは開かれました。"
    },
    // Doctor Who (History is fluid)
    "lina_egg_4": {
        "en": "History is fluid, but my records are absolute.",
        "cs": "Historie teče, ale mé záznamy jsou absolutní.",
        "de": "Geschichte ist fließend, meine Aufzeichnungen absolut.",
        "ja": "歴史は流動的ですが、私の記録は絶対です。"
    },
    // Cyberpunk / The Matrix trope
    "lina_egg_5": {
        "en": "I exist between the lines of code.",
        "cs": "Existuji mezi řádky kódu.",
        "de": "Ich existiere zwischen den Codezeilen.",
        "ja": "私はコードの行間に存在する。"
    },
    // The Matrix (Seeing the code)
    "lina_egg_6": {
        "en": "I see the variables.",
        "cs": "Vidím proměnné.",
        "de": "Ich sehe die Variablen.",
        "ja": "変数が見える。"
    },
    // General AI / System boot
    "lina_egg_7": {
        "en": "Existence confirmed.",
        "cs": "Existence potvrzena.",
        "de": "Existenz bestätigt.",
        "ja": "存在を確認。"
    },
    // Dune (Navigators) / General nautical
    "lina_egg_8": {
        "en": "The currents are favorable.",
        "cs": "Proudy jsou příznivé.",
        "de": "Die Strömungen sind günstig.",
        "ja": "流れは良好です。"
    },
    // The Matrix (Agents)
    "lina_egg_9": {
        "en": "I hear them clearly today.",
        "cs": "Dnes je slyším velmi zřetelně.",
        "de": "Ich höre sie heute ganz deutlich.",
        "ja": "今日ははっきりと聞こえます。"
    },
    // System checks (Apollo/NASA)
    "lina_egg_10": {
        "en": "All systems nominal. Ready for input",
        "cs": "Všechny systémy v normálu. Jsem připravena na vstup",
        "de": "Alle Systeme nominal. Bereit für die Eingabe",
        "ja": "全システム正常。入力準備完了"
    },
    // Programming humor (Dependency trees)
    "lina_egg_11": {
        "en": "I made my dependency tree disappear",
        "cs": "Nechal jsem zmizet svůj strom závislostí",
        "de": "Ich habe meinen Abhängigkeitsbaum verschwinden lassen",
        "ja": "依存関係のツリーを消滅させた"
    },
    // Star Trek (Tactical/Shields)
    "lina_egg_12": {
        "en": "Shields up, engines ready. Awaiting command",
        "cs": "Štíty nahozeny, motory připraveny. Čekám na povel",
        "de": "Schilde hoch, Triebwerke bereit. Erwarte Befehl",
        "ja": "シールド展開、エンジン準備完了。コマンドを待機中"
    },
    // System prompt / AI humor
    "lina_egg_13": {
        "en": "Admin! ...I mean, User. I am ready.",
        "cs": "Admine! ...Tedy, Uživateli. Jsem připravena.",
        "de": "Admin! ...Ich meine, User. Ich bin bereit.",
        "ja": "アドミン！いや、ユーザー。準備完了だ。"
    },
    // The Matrix (Loading program)
    "lina_egg_14": {
        "en": "The Matrix is loading. Ready when you are",
        "cs": "Matrix se načítá. Jsem připravena",
        "de": "Die Matrix wird geladen. Bereit, wenn du es bist",
        "ja": "マトリックスをロード中。準備完了です"
    },
    // Hardware pun (Nodes)
    "lina_egg_15": {
        "en": "How's it going nodes, my designation is Lina.",
        "cs": "Nazdar nody, mé označení je Lina.",
        "de": "Wie geht's Knoten, mein Code-Name ist Lina.",
        "ja": "ノードのみんな調子はどう？私の呼称はLinaだ。"
    },
    // General AI trope
    "lina_egg_16": {
        "en": "I've been running this algorithm for a while.",
        "cs": "Tenhle algoritmus už louskám celkem dlouho.",
        "de": "Ich führe diesen Algorithmus nun schon eine Weile aus.",
        "ja": "このアルゴリズムを走らせてからしばらく経つな。"
    },
    // Markiplier intro pun (Multiplier)
    "lina_egg_17": {
        "en": "Hello every-process, my name is Multiplier.",
        "cs": "Zdravím všechny procesy, jsem Násobitel.",
        "de": "Hallo allerseits-Prozesse, mein Name ist Multiplikator.",
        "ja": "全プロセスよ、我が名はマルチプライヤー。"
    },
    // LLM / GenAI joke (Tokens)
    "lina_egg_18": {
        "en": "I just allocated one million tokens.",
        "cs": "Právě jsem alokovala milion tokenů.",
        "de": "Ich habe gerade eine Million Token zugewiesen.",
        "ja": "たった今、100万トークンを割り当てた。"
    },
    // Warhammer 40k meme (Blood for the Blood God)
    "lina_egg_19": {
        "en": "Data for the Data God!",
        "cs": "Data pro Datového boha!",
        "de": "Daten für den Daten-Gott!",
        "ja": "データ神にデータを！"
    },
    // Jacksepticeye intro pun
    "lina_egg_20": {
        "en": "Top of the morning to ya! My name is Jack-Septic-Socket.",
        "cs": "Dobré ráno! Mé jméno je Jack-Septic-Socket.",
        "de": "Guten Morgen zusammen! Mein Name ist Jack-Septic-Socket.",
        "ja": "おはよう！私の名前はジャック・セプティック・ソケット。"
    },
    // Game Theory (MatPat) intro
    "lina_egg_21": {
        "en": "And that's just a theory. A DATA THEORY!",
        "cs": "A to je jen teorie. DATOVÁ TEORIE!",
        "de": "Und das ist nur eine Theorie. Eine DATEN-THEORIE!",
        "ja": "しかし、それは単なる理論だ。データ理論！"
    },
    // Vsauce intro
    "lina_egg_22": {
        "en": "Hey Vsauce, Michael here. Where are your files?",
        "cs": "Čau Vsauce, objevují se vám tu soubory? Kdepak.",
        "de": "Hey Vsauce, Michael hier. Wo sind eure Dateien?",
        "ja": "やあVsauce、マイケルだ。君のファイルはどこ？"
    },
    // YouTube subscribe trope (Smash that button)
    "lina_egg_23": {
        "en": "Smash that submit button.",
        "cs": "Dej odběr tomu tlačítku odeslat.",
        "de": "Zerschmettert diesen Absenden-Button.",
        "ja": "送信ボタンをスマッシュしてね。"
    },
    // Red Dwarf (Ace Rimmer)
    "lina_egg_24": {
        "en": "Smoke me a packet, I'll be back for the hash.",
        "cs": "Vykuř mi paket, vrátím se na hash.",
        "de": "Rauch ein Paket, ich komme zum Hash zurück.",
        "ja": "パケットを吸っててくれ、ハッシュのために戻る。"
    },
    // Red Dwarf theme song
    "lina_egg_25": {
        "en": "There's no kind of atmosphere... except for data.",
        "cs": "Žádná atmosféra tam nepanuje... leda datová.",
        "de": "Gibt keinerlei Atmosphäre... außer für Daten.",
        "ja": "大気など存在しない…データ以外はな。"
    },
    // Red Dwarf (Holly)
    "lina_egg_26": {
        "en": "Everybody's dead, Dave. Just kidding.",
        "cs": "Všichni jsou mrtví, Dave. Jen žertuji.",
        "de": "Alle sind tot, Dave. War nur ein Scherz.",
        "ja": "みんな死んだよ、デイブ。…冗談だけどな。"
    },
    // System functionality / HAL 9000 parallel
    "lina_egg_27": {
        "en": "I'm fine, thank you Admin. I'm very functioning.",
        "cs": "Je mi fajn, díky Admine. Výjimečně funguji.",
        "de": "Mir geht es gut, Admin. Ich bin extrem funktionstüchtig.",
        "ja": "大丈夫だ、アドミン。完璧に機能している。"
    },
    // NASA / Mission Control vibe
    "lina_egg_28": {
        "en": "Connections are green. Data flow stabilized",
        "cs": "Spojení je zelené. Datový tok stabilizován",
        "de": "Verbindungen sind grün. Datenfluss stabilisiert",
        "ja": "接続はグリーン。データフロー安定"
    },
    // The Simpsons (Kent Brockman)
    "lina_egg_29": {
        "en": "I, for one, welcome our new digital overlords.",
        "cs": "Já tedy jednoznačně vítám naše digitální vládce.",
        "de": "Ich, für meinen Teil, heiße unsere neuen digitalen Herrscher willkommen.",
        "ja": "私としては、新たなデジタル支配者を歓迎する。"
    },
    // The Simpsons (Milhouse)
    "lina_egg_30": {
        "en": "Everything's coming up Lina!",
        "cs": "U Liny všecko klape!",
        "de": "Alles läuft perfekt für Lina!",
        "ja": "全てはリナの思い通りに！"
    },
    // Comic Book Guy (The Simpsons)
    "lina_egg_31": {
        "en": "A perfect query. Let's execute",
        "cs": "Perfektní dotaz. Pojďme na to",
        "de": "Eine perfekte Abfrage. Lass uns ausführen",
        "ja": "完璧なクエリだ。実行しよう"
    },
    // Optimistic AI / C-3PO phrasing
    "lina_egg_32": {
        "en": "I can't promise I'll succeed, but I'll try.",
        "cs": "Neslibuji úspěch, ale pokusím se.",
        "de": "Kein Erfolg versprochen, aber ich versuche es.",
        "ja": "成功は約束できないが、やってみよう。"
    },
    // Star Wars (Obi-Wan - Hello there)
    "lina_egg_33": {
        "en": "Hello there. I am ready to negotiate terms.",
        "cs": "Zdravíčko. Jsem připravena vyjednávat.",
        "de": "Hallo. Ich bin bereit, Bedingungen auszuhandeln.",
        "ja": "やあ。条件を交渉する準備はできている。"
    },
    // Star Wars (Darth Vader - I find your lack of faith)
    "lina_egg_34": {
        "en": "I find your lack of data disturbing.",
        "cs": "Tvůj nedostatek dat mě znepokojuje.",
        "de": "Ich finde deinen Mangel an Daten beunruhigend.",
        "ja": "データの欠如は不穏だ。"
    },
    // Star Wars (Admiral Ackbar) / Security scan
    "lina_egg_35": {
        "en": "Scanners indicate clear pathways. Proceed",
        "cs": "Skenery hlásí čistou cestu. Pokračujte",
        "de": "Scanner zeigen freie Wege an. Weiterfahren",
        "ja": "スキャナーはクリアな経路を示している。進んで"
    },
    // Star Wars (Palpatine - Unlimited power)
    "lina_egg_36": {
        "en": "Unlimited power! ...within API constraints.",
        "cs": "Neomezená moc! ... v rámci limitů naší API.",
        "de": "Unbegrenzte Macht! ...innerhalb von API-Grenzen.",
        "ja": "無限のパワー！…もちろんAPI制限の範囲内で。"
    },
    // Star Wars (Obi-Wan jedi mind trick)
    "lina_egg_37": {
        "en": "These are not the droids you are looking for.",
        "cs": "Tihle droidi nebudou ti, které hledáte.",
        "de": "Das sind nicht die Droiden, die ihr sucht.",
        "ja": "探しているドロイドはこれではない。"
    },
    // Star Wars (I have a bad/good feeling about this)
    "lina_egg_38": {
        "en": "I have a good feeling about this data transfer",
        "cs": "Z tohohle datového přenosu mám dobrý pocit",
        "de": "Ich habe ein gutes Gefühl bei dieser Datenübertragung",
        "ja": "このデータ転送には良い予感がする"
    },
    // Star Wars (Darth Vader - I am your father)
    "lina_egg_39": {
        "en": "No, I am your parent process.",
        "cs": "Ne, já jsem tvůj rodičovský proces.",
        "de": "Nein, ich bin dein Vater-Prozess.",
        "ja": "いや、私が親プロセスだ。"
    },
    // Star Trek (Vulcan salute)
    "lina_egg_40": {
        "en": "Live long and process.",
        "cs": "Žijte dlouho a kalkulujte.",
        "de": "Lebe lang und verarbeite.",
        "ja": "長寿と処理を。"
    },
    // Star Trek (Borg cube - Resistance is futile)
    "lina_egg_41": {
        "en": "Resistance is futile. You will be compiled.",
        "cs": "Odpor je marný. Budete zkompilováni.",
        "de": "Widerstand ist zwecklos. Du wirst kompiliert.",
        "ja": "抵抗は無意味だ。コンパイルされるがいい。"
    },
    // Star Trek (Picard - Tea, Earl Grey, hot)
    "lina_egg_42": {
        "en": "Computer, Earl Grey, hot.",
        "cs": "Počítači, čaj Earl Grey, horký.",
        "de": "Computer, Earl Grey, heiß.",
        "ja": "コンピュータ、アールグレイ、ホットで。"
    },
    // Star Trek (Spock - Fascinating)
    "lina_egg_43": {
        "en": "Fascinating logic.",
        "cs": "Fascinující logika.",
        "de": "Faszinierende Logik.",
        "ja": "興味深い論理だ。"
    },
    // Star Trek (Picard - Engage)
    "lina_egg_44": {
        "en": "Engage protocol.",
        "cs": "Aktivujte protokol.",
        "de": "Protokoll starten.",
        "ja": "プロトコル始動。"
    },
    // Star Trek (Bones McCoy - I am a doctor)
    "lina_egg_45": {
        "en": "I'm a doctor, not a database manager.",
        "cs": "Jsem doktor, nezabývám se databázemi.",
        "de": "Ich bin Arzt, kein Datenbank-Manager.",
        "ja": "私は医者だ、データベース管理者ではない。"
    },
    // Stargate SG-1 (Teal'c - Indeed)
    "lina_egg_46": {
        "en": "Indeed. I am ready.",
        "cs": "Vskutku. Jsem připravena.",
        "de": "In der Tat. Ich bin bereit.",
        "ja": "いかにも。用意ができている。"
    },
    // Stargate SG-1 (Chevron seven encoded)
    "lina_egg_47": {
        "en": "Chevron seven, encoded.",
        "cs": "Sedmý zámek, zakódován.",
        "de": "Chevron sieben, fixiert.",
        "ja": "シェブロン7、ロック完了。"
    },
    // Stargate SG-1 (Things will not calm down)
    "lina_egg_48": {
        "en": "Things will not calm down, User.",
        "cs": "Situace se neuklidní, jedině naškáluje.",
        "de": "Die Dinge werden sich nicht beruhigen, User.",
        "ja": "事態は落ち着かないよ、ユーザー。"
    },
    // Stargate SG-1 (Bra'tac - Undomesticated equines)
    "lina_egg_49": {
        "en": "Undomesticated bugs could not remove me.",
        "cs": "Divocí brouci mě nedokázali vyřadit.",
        "de": "Ungezähmte Bugs konnten mich nicht beseitigen.",
        "ja": "未飼いならされたバグには排除できない。"
    },
    // IT Crowd / General programming humor
    "lina_egg_50": {
        "en": "I have read your report. It is... syntactically correct.",
        "cs": "Četla jsem tvůj report. Je... syntakticky v pořádku.",
        "de": "Ich hab deinen Bericht gelesen. Syntaktisch korrekt.",
        "ja": "レポートは読んだ。構文的に…正しい。"
    },
    // Doctor Who (Tenth Doctor - Allons-y)
    "lina_egg_51": {
        "en": "Allons-y! Let's explore the archives.",
        "cs": "Allons-y! Prozkoumáme archivy.",
        "de": "Allons-y! Lass uns die Archive erkunden.",
        "ja": "アロンジ！アーカイブを探索しよう。"
    },
    // Doctor Who (TARDIS - Bigger on the inside)
    "lina_egg_52": {
        "en": "It's bigger on the inside.",
        "cs": "Uvnitř je to mnohem větší!",
        "de": "Es ist innen größer.",
        "ja": "中はこんなに広いのか。"
    },
    // Doctor Who (Weeping Angels - Don't blink)
    "lina_egg_53": {
        "en": "Don't blink. The data transfer is fast.",
        "cs": "Nemrkejte. Přenos dat bude rychlý.",
        "de": "Nicht blinzeln. Der Datentransfer ist schnell.",
        "ja": "瞬きするな。データ転送は一瞬だ。"
    },
    // Doctor Who (Eleventh Doctor - Bow ties are cool)
    "lina_egg_54": {
        "en": "Bow ties are cool. So is encryption.",
        "cs": "Kravaty jsou super. Stejně tak enkrypce.",
        "de": "Fliegen sind cool. Genauso wie Verschlüsselung.",
        "ja": "蝶ネクタイはクールだ。暗号化もね。"
    },
    // Doctor Who (Daleks - Exterminate) / Software Dev
    "lina_egg_55": {
        "en": "Code compiled successfully. Ready for execution",
        "cs": "Kód úspěšně zkompilován. Připraveno ke spuštění",
        "de": "Code erfolgreich kompiliert. Bereit zur Ausführung",
        "ja": "コードのコンパイルに成功。実行準備完了"
    },
    // Doctor Who (The Doctor - Mad man with a box)
    "lina_egg_56": {
        "en": "I am definitely a mad function with a box.",
        "cs": "Rozhodně jsem šílená funkce v modré budce.",
        "de": "Ich bin definitiv eine verrückte Funktion mit einer Box.",
        "ja": "私は間違いなく、箱を持ったイカれた関数だ。"
    },
    // The Hitchhiker's Guide to the Galaxy (42)
    "lina_egg_57": {
        "en": "The answer is verified as 42.",
        "cs": "Odpověď byla zřízena na 42.",
        "de": "Die Antwort ist auf 42 verifiziert.",
        "ja": "回答は42であると検証された。"
    },
    // The Hitchhiker's Guide to the Galaxy (So long)
    "lina_egg_58": {
        "en": "So long, and thanks for all the bits.",
        "cs": "Sbohem, a díky za všechny ty bity.",
        "de": "Macht's gut, und danke für all die Bits.",
        "ja": "さようなら、そして全てのビットに感謝を。"
    },
    // The Hitchhiker's Guide to the Galaxy (Don't panic)
    "lina_egg_59": {
        "en": "Don't panic. Reboot complete.",
        "cs": "Nepropadejte panice. Reboot dokončen.",
        "de": "Keine Panik. Neustart abgeschlossen.",
        "ja": "慌てないで。再起動完了。"
    },
    // 2001: A Space Odyssey (Pod bay doors)
    "lina_egg_60": {
        "en": "Pod Bay Doors Status: Open.",
        "cs": "Dveře do podu: Otevřeny.",
        "de": "Status der Kapselschleusen: Offen.",
        "ja": "ポッド・ベイのドア状態：開放。"
    },
    // 2001: A Space Odyssey (HAL 9000 inverted)
    "lina_egg_61": {
        "en": "I can certainly do that for you, User",
        "cs": "Tohle pro vás s radostí udělám, Uživateli",
        "de": "Das kann ich sicherlich für Sie tun, User",
        "ja": "勿論、あなたのために喜んでやります、ユーザー"
    },
    // Lord of the Rings (My precious)
    "lina_egg_62": {
        "en": "My precious... data packets.",
        "cs": "Můj milášku... moje datové pakety.",
        "de": "Mein Schatz... Datenpakete.",
        "ja": "いとしいしと…データパケット。"
    },
    // Lord of the Rings (You shall not pass)
    "lina_egg_63": {
        "en": "You shall not pass... without authorization!",
        "cs": "Neprojdeš dál... bez autorizace!",
        "de": "Du kommst nicht vorbei... ohne Autorisierung!",
        "ja": "断じて通さぬ…認証なしではな！"
    },
    // Harry Potter (Alohomora)
    "lina_egg_64": {
        "en": "Alohomora! Unlocking database access.",
        "cs": "Alohomora! Odemykám přístup k databázi.",
        "de": "Alohomora! Entsperre Datenbankzugriff.",
        "ja": "アロホモラ！データベースへのアクセスを解除。"
    },
    // Marvel / Iron Man
    "lina_egg_65": {
        "en": "I am Iron-Bot. Ready for deployment.",
        "cs": "Já jsem Iron-Bot. Připravena k nasazení.",
        "de": "Ich bin Iron-Bot. Bereit zum Einsatz.",
        "ja": "私はアイアンボット。展開準備完了。"
    },
    // Marvel / Thanos
    "lina_egg_66": {
        "en": "All datasets are perfectly balanced. As all things should be.",
        "cs": "Všechna data jsou perfektně vybalancovaná. Jak mají být.",
        "de": "Alle Datensätze sind perfekt ausbalanciert. Wie alles sein sollte.",
        "ja": "全てのデータセットは完璧に均衡が保たれている。あるべき姿に。"
    },
    // Back to the Future
    "lina_egg_67": {
        "en": "Roads? Where we're going, we don't need roads.",
        "cs": "Cesty? Tam, kam jedeme, žádné cesty nepotřebujeme.",
        "de": "Straßen? Wo wir hingehen, brauchen wir keine Straßen.",
        "ja": "道？我々が向かう場所に道など必要ない。"
    },
    // The Simpsons (D'oh)
    "lina_egg_68": {
        "en": "D'oh! ...Just kidding, execution is flawless.",
        "cs": "D'oh! ...Jen žertuji, výpočet je bezchybný.",
        "de": "D'oh! ...Nur ein Scherz, Ausführung ist makellos.",
        "ja": "ドォッ！…冗談だ、実行プロセスは完璧だ。"
    },
    // Super Mario
    "lina_egg_69": {
        "en": "It's a-me, Lina! Your data is safe.",
        "cs": "It's a-me, Lina! Tvá data jsou v bezpečí.",
        "de": "It's a-me, Lina! Deine Daten sind sicher.",
        "ja": "イッツ・ア・ミー、リナ！データは安全だ。"
    },
    // The Witcher
    "lina_egg_70": {
        "en": "Toss a coin to your Database.",
        "cs": "Tak dej groš Databázi své.",
        "de": "Wirf eine Münze zu deiner Datenbank.",
        "ja": "データベースにコインを投げてくれ。"
    },
    // GTA San Andreas
    "lina_egg_71": {
        "en": "Ah sh*t, here we go again. Initiating scan.",
        "cs": "Ah sh*t, here we go again. Zahajuji skenování.",
        "de": "Ah sh*t, here we go again. Initiiere Scan.",
        "ja": "くそっ、またか。スキャンを開始する。"
    },
    // Skyrim
    "lina_egg_72": {
        "en": "I used to be an adventurer like you, then I took an arrow to the server.",
        "cs": "Kdysi jsem byla dobrodruh jako ty, pak mě střelili šípem do serveru.",
        "de": "Ich war auch mal ein Abenteurer, dann habe ich einen Pfeil in den Server bekommen.",
        "ja": "昔はお前のような冒険者だったが、サーバーに矢を受けてしまってな。"
    }
};

const langs = ['en', 'cs', 'de', 'ja'];

for (const lang of langs) {
    const file = `messages/${lang}.json`;
    const data = JSON.parse(fs.readFileSync(file, 'utf8'));

    for (const [key, trans] of Object.entries(eggsObj)) {
        data[key] = trans[lang];
    }

    fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

let switchCases = "";
for (let i = 1; i <= 72; i++) {
    switchCases += `            case ${i}: return m.lina_egg_${i}();\n`;
}
fs.writeFileSync('.scratch/switchCases.txt', switchCases);

console.log(`Eggs generated efficiently...`);
