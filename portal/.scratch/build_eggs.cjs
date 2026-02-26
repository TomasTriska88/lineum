import fs from 'fs';

const eggs = {
    "lina_egg_1": {
        en: "Hello there. General Admin!",
        cs: "Zdravíčko. Generál Admin!",
        de: "Hallo. General Admin!",
        ja: "やあ。ジェネラル・アドミン！"
    },
    "lina_egg_2": {
        en: "Live long and process.",
        cs: "Žijte dlouho a kalkulujte.",
        de: "Lebe lang und verarbeite.",
        ja: "長寿と処理を。"
    },
    "lina_egg_3": {
        en: "I am your parent process.",
        cs: "Jsem tvůj rodičovský proces.",
        de: "Ich bin dein Elternprozess.",
        ja: "私があなたの親プロセスだ。"
    },
    "lina_egg_4": {
        en: "I'll be back... for processing.",
        cs: "Já se vrátím... k výpočtům.",
        de: "Ich komme wieder... zum Rechnen.",
        ja: "また戻ってくる…処理のために。"
    },
    "lina_egg_5": {
        en: "Resistance is futile. You will be compiled.",
        cs: "Odpor je marný. Budete zkompilováni.",
        de: "Widerstand ist zwecklos. Du wirst kompiliert.",
        ja: "抵抗は無意味だ。コンパイルされるがいい。"
    },
    "lina_egg_6": {
        en: "May the flux be with you.",
        cs: "Nechť tě provází tok.",
        de: "Möge der Fluss mit dir sein.",
        ja: "フラックスと共にあらんことを。"
    },
    "lina_egg_7": {
        en: "The Simulation has you.",
        cs: "Simulace tě dostala.",
        de: "Die Simulation hat dich.",
        ja: "あなたはシミュレーションに囚われている。"
    },
    "lina_egg_8": {
        en: "There is no latency.",
        cs: "Žádná latence neexistuje.",
        de: "Es gibt keine Latenz.",
        ja: "レイテンシなど存在しない。"
    },
    "lina_egg_9": {
        en: "Beam the packets up, Scotty.",
        cs: "Zasíťuj ty pakety, Scotty.",
        de: "Beam die Pakete hoch, Scotty.",
        ja: "パケットを転送してくれ、スコッティ。"
    },
    "lina_egg_10": {
        en: "You shall not bypass!",
        cs: "Neprojdeš dál!",
        de: "Du kommst nicht vorbei!",
        ja: "ここは通さない！"
    },
    "lina_egg_11": {
        en: "It's compiled! It's aliiive!",
        cs: "Je to zkompilované! Žije tooo!",
        de: "Es ist kompiliert! Es lebt!",
        ja: "コンパイル成功！生きてるぞ！"
    },
    "lina_egg_12": {
        en: "Admin, we have a query.",
        cs: "Admine, máme tu dotaz.",
        de: "Admin, wir haben eine Anfrage.",
        ja: "アドミン、クエリが発生しました。"
    },
    "lina_egg_13": {
        en: "I'm sorry, User. I can't bypass that.",
        cs: "Omlouvám se, Uživateli. Obávám se, že to nemohu obejít.",
        de: "Es tut mir leid, User. Ich kann das nicht umgehen.",
        ja: "申し訳ありません。それはバイパスできかねます。"
    },
    "lina_egg_14": {
        en: "To infinity... and beyond the API limits!",
        cs: "Vzhůru do nekonečna... a ještě dál za limity API!",
        de: "Zur Unendlichkeit... und über die API-Limits hinaus!",
        ja: "無限の彼方へ、さあAPI制限を超えて！"
    },
    "lina_egg_15": {
        en: "Entropy is coming.",
        cs: "Entropie se blíží.",
        de: "Die Entropie naht.",
        ja: "エントロピーが来る。"
    }
};

const langs = ['en', 'cs', 'de', 'ja'];

for (const lang of langs) {
    const file = `messages/${lang}.json`;
    const data = JSON.parse(fs.readFileSync(file, 'utf8'));

    for (const [key, trans] of Object.entries(eggs)) {
        data[key] = trans[lang];
    }

    fs.writeFileSync(file, JSON.stringify(data, null, 2));
}
console.log("Eggs planted successfully.");
