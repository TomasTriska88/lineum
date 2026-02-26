import fs from 'fs';

let file = fs.readFileSync('.scratch/build_eggs_all.mjs', 'utf8');
const lines = file.split('\n');

// 1. Add Rule 5
const rule4Idx = lines.findIndex(l => l.includes('4. KEEP IT SUBTLE YET GEEKY:'));
if (rule4Idx !== -1) {
    const endRule4Idx = lines.findIndex((l, i) => i > rule4Idx && l.includes('============================================================================'));
    if (endRule4Idx !== -1) {
        lines.splice(endRule4Idx, 0,
            ' * ',
            ' * 5. NO UNCERTAINTY OR HESITATION:',
            ' *    The AI should never sound doubtful about its capabilities. Avoid phrases',
            ' *    like "I\'ll try", "I hope", "I can\'t promise", etc.',
            ' *    Always use confident, absolute statements like "Commencing calculation".'
        );
    }
}

// 2. Replace lina_egg_32
for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('lina_egg_32') && lines[i].includes('Optimistic AI')) {
        let start = i;
        while (!lines[start + 1].includes('lina_egg_33')) {
            if (lines[start + 1].includes('"en":')) lines[start + 1] = '        "en": "I am fluent in over six million forms of communication.",';
            if (lines[start + 1].includes('"cs":')) lines[start + 1] = '        "cs": "Hbitě ovládám přes šest milionů forem komunikace.",';
            if (lines[start + 1].includes('"de":')) lines[start + 1] = '        "de": "Ich beherrsche über sechs Millionen Kommunikationsformen.",';
            if (lines[start + 1].includes('"ja":')) lines[start + 1] = '        "ja": "600万以上のコミュニケーション形態に堪能です。"';
            start++;
        }
        break;
    }
}

// 3. Append eggs 62-72
const objEndIdx = lines.findIndex((l, i) => l.trim() === '};' && i > 100);
if (objEndIdx !== -1) {
    // Make sure we are at the end of the object
    if (lines[objEndIdx - 1].includes('lina_egg_61')) {
        // do nothing since there's an ending bracket for the item before the main closing
    }

    // Add a comma to the last object property
    for (let i = objEndIdx - 1; i > 0; i--) {
        if (lines[i].includes('}')) {
            lines[i] = lines[i] + ',';
            break;
        }
    }

    lines.splice(objEndIdx, 0,
        '    // Lord of the Rings (My precious)',
        '    "lina_egg_62": {',
        '        "en": "My precious... data packets.",',
        '        "cs": "Můj milášku... moje datové pakety.",',
        '        "de": "Mein Schatz... Datenpakete.",',
        '        "ja": "いとしいしと…データパケット。"',
        '    },',
        '    // Lord of the Rings (You shall not pass)',
        '    "lina_egg_63": {',
        '        "en": "You shall not pass... without authorization!",',
        '        "cs": "Neprojdeš dál... bez autorizace!",',
        '        "de": "Du kommst nicht vorbei... ohne Autorisierung!",',
        '        "ja": "断じて通さぬ…認証なしではな！"',
        '    },',
        '    // Harry Potter (Alohomora)',
        '    "lina_egg_64": {',
        '        "en": "Alohomora! Unlocking database access.",',
        '        "cs": "Alohomora! Odemykám přístup k databázi.",',
        '        "de": "Alohomora! Entsperre Datenbankzugriff.",',
        '        "ja": "アロホモラ！データベースへのアクセスを解除。"',
        '    },',
        '    // Marvel / Iron Man',
        '    "lina_egg_65": {',
        '        "en": "I am Iron-Bot. Ready for deployment.",',
        '        "cs": "Já jsem Iron-Bot. Připravena k nasazení.",',
        '        "de": "Ich bin Iron-Bot. Bereit zum Einsatz.",',
        '        "ja": "私はアイアンボット。展開準備完了。"',
        '    },',
        '    // Marvel / Thanos',
        '    "lina_egg_66": {',
        '        "en": "All datasets are perfectly balanced. As all things should be.",',
        '        "cs": "Všechna data jsou perfektně vybalancovaná. Jak mají být.",',
        '        "de": "Alle Datensätze sind perfekt ausbalanciert. Wie alles sein sollte.",',
        '        "ja": "全てのデータセットは完璧に均衡が保たれている。あるべき姿に。"',
        '    },',
        '    // Back to the Future',
        '    "lina_egg_67": {',
        '        "en": "Roads? Where we\'re going, we don\'t need roads.",',
        '        "cs": "Cesty? Tam, kam jedeme, žádné cesty nepotřebujeme.",',
        '        "de": "Straßen? Wo wir hingehen, brauchen wir keine Straßen.",',
        '        "ja": "道？我々が向かう場所に道など必要ない。"',
        '    },',
        '    // The Simpsons (D\'oh)',
        '    "lina_egg_68": {',
        '        "en": "D\'oh! ...Just kidding, execution is flawless.",',
        '        "cs": "D\'oh! ...Jen žertuji, výpočet je bezchybný.",',
        '        "de": "D\'oh! ...Nur ein Scherz, Ausführung ist makellos.",',
        '        "ja": "ドォッ！…冗談だ、実行プロセスは完璧だ。"',
        '    },',
        '    // Super Mario',
        '    "lina_egg_69": {',
        '        "en": "It\'s a-me, Lina! Your data is safe.",',
        '        "cs": "It\'s a-me, Lina! Tvá data jsou v bezpečí.",',
        '        "de": "It\'s a-me, Lina! Deine Daten sind sicher.",',
        '        "ja": "イッツ・ア・ミー、リナ！データは安全だ。"',
        '    },',
        '    // The Witcher',
        '    "lina_egg_70": {',
        '        "en": "Toss a coin to your Database.",',
        '        "cs": "Tak dej groš Databázi své.",',
        '        "de": "Wirf eine Münze zu deiner Datenbank.",',
        '        "ja": "データベースにコインを投げてくれ。"',
        '    },',
        '    // GTA San Andreas',
        '    "lina_egg_71": {',
        '        "en": "Ah sh*t, here we go again. Initiating scan.",',
        '        "cs": "Ah sh*t, here we go again. Zahajuji skenování.",',
        '        "de": "Ah sh*t, here we go again. Initiiere Scan.",',
        '        "ja": "くそっ、またか。スキャンを開始する。"',
        '    },',
        '    // Skyrim',
        '    "lina_egg_72": {',
        '        "en": "I used to be an adventurer like you, then I took an arrow to the server.",',
        '        "cs": "Kdysi jsem byla dobrodruh jako ty, pak mě střelili šípem do serveru.",',
        '        "de": "Ich war auch mal ein Abenteurer, dann habe ich einen Pfeil in den Server bekommen.",',
        '        "ja": "昔はお前のような冒険者だったが、サーバーに矢を受けてしまってな。"',
        '    }'
    );
}

// 4. Update the switchCase generation from 61 to 72
for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('for (let i = 1; i <= 61; i++) {')) {
        lines[i] = 'for (let i = 1; i <= 72; i++) {';
        break;
    }
}

fs.writeFileSync('.scratch/build_eggs_all.mjs', lines.join('\n'));
console.log('Script updated with 72 eggs by patching lines cleanly.');
