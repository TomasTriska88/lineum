import fs from 'fs';

let content = fs.readFileSync('src/lib/components/ResonanceDeck.svelte', 'utf8');

// Replace the two occurrences of 61 with 72
content = content.replace(/Math\.floor\(Math\.random\(\) \* 61\) \+ 1/g, 'Math.floor(Math.random() * 72) + 1');

// Replace the switch statement body
const switchStart = content.indexOf('switch (index) {');
const switchEnd = content.indexOf('let loadingMessageId', switchStart);

if (switchStart !== -1 && switchEnd !== -1) {
    let newSwitchBlock = 'switch (index) {\n';
    for (let i = 1; i <= 72; i++) {
        newSwitchBlock += `            case ${i}:\n                return m.lina_egg_${i}();\n`;
    }
    newSwitchBlock += '            default:\n                return m.lina_egg_1();\n        }\n    }\n\n    ';

    // We need to find the exact end of the old switch block.
    // getEggText function ends after the switch statement.
    const beforeSwitch = content.substring(0, switchStart);
    const afterSwitch = content.substring(switchEnd);

    fs.writeFileSync('src/lib/components/ResonanceDeck.svelte', beforeSwitch + newSwitchBlock + 'let loadingMessageId' + afterSwitch.substring(20)); // substring removes "let loadingMessageId" from afterSwitch so we don't double it. Actually better to just use replace using index
} else {
    console.error("Could not find switch block.");
}

console.log('Svelte patched');
