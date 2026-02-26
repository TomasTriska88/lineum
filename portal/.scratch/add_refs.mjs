import fs from 'fs';

let content = fs.readFileSync('.scratch/build_eggs_all.mjs', 'utf8');

const refs = {
    1: "// General Sci-fi / Operations",
    2: "// Sci-fi trope (Stabilizing the flow)",
    3: "// General fantasy/RPG trope",
    4: "// Doctor Who (History is fluid)",
    5: "// Cyberpunk / The Matrix trope",
    6: "// The Matrix (Seeing the code)",
    7: "// General AI / System boot",
    8: "// Dune (Navigators) / General nautical",
    9: "// The Matrix (Agents)",
    10: "// System checks (Apollo/NASA)",
    11: "// Programming humor (Dependency trees)",
    12: "// Star Trek (Tactical/Shields)",
    13: "// System prompt / AI humor",
    14: "// The Matrix (Loading program)",
    15: "// Hardware pun (Nodes)",
    16: "// General AI trope",
    17: "// Markiplier intro pun (Multiplier)",
    18: "// LLM / GenAI joke (Tokens)",
    19: "// Warhammer 40k meme (Blood for the Blood God)",
    20: "// Jacksepticeye intro pun",
    21: "// Game Theory (MatPat) intro",
    22: "// Vsauce intro",
    23: "// YouTube subscribe trope (Smash that button)",
    24: "// Red Dwarf (Ace Rimmer)",
    25: "// Red Dwarf theme song",
    26: "// Red Dwarf (Holly)",
    27: "// System functionality / HAL 9000 parallel",
    28: "// NASA / Mission Control vibe",
    29: "// The Simpsons (Kent Brockman)",
    30: "// The Simpsons (Milhouse)",
    31: "// Comic Book Guy (The Simpsons)",
    32: "// Optimistic AI / C-3PO phrasing",
    33: "// Star Wars (Obi-Wan - Hello there)",
    34: "// Star Wars (Darth Vader - I find your lack of faith)",
    35: "// Star Wars (Admiral Ackbar) / Security scan",
    36: "// Star Wars (Palpatine - Unlimited power)",
    37: "// Star Wars (Obi-Wan jedi mind trick)",
    38: "// Star Wars (I have a bad/good feeling about this)",
    39: "// Star Wars (Darth Vader - I am your father)",
    40: "// Star Trek (Vulcan salute)",
    41: "// Star Trek (Borg cube - Resistance is futile)",
    42: "// Star Trek (Picard - Tea, Earl Grey, hot)",
    43: "// Star Trek (Spock - Fascinating)",
    44: "// Star Trek (Picard - Engage)",
    45: "// Star Trek (Bones McCoy - I am a doctor)",
    46: "// Stargate SG-1 (Teal'c - Indeed)",
    47: "// Stargate SG-1 (Chevron seven encoded)",
    48: "// Stargate SG-1 (Things will not calm down)",
    49: "// Stargate SG-1 (Bra'tac - Undomesticated equines)",
    50: "// IT Crowd / General programming humor",
    51: "// Doctor Who (Tenth Doctor - Allons-y)",
    52: "// Doctor Who (TARDIS - Bigger on the inside)",
    53: "// Doctor Who (Weeping Angels - Don't blink)",
    54: "// Doctor Who (Eleventh Doctor - Bow ties are cool)",
    55: "// Doctor Who (Daleks - Exterminate) / Software Dev",
    56: "// Doctor Who (The Doctor - Mad man with a box)",
    57: "// The Hitchhiker's Guide to the Galaxy (42)",
    58: "// The Hitchhiker's Guide to the Galaxy (So long)",
    59: "// The Hitchhiker's Guide to the Galaxy (Don't panic)",
    60: "// 2001: A Space Odyssey (Pod bay doors)",
    61: "// 2001: A Space Odyssey (HAL 9000 inverted)"
};

for (const [key, ref] of Object.entries(refs)) {
    const searchStr = `    "lina_egg_${key}": {`;
    if (!content.includes(ref)) {
        content = content.replace(searchStr, `    ${ref}\n${searchStr}`);
    }
}

fs.writeFileSync('.scratch/build_eggs_all.mjs', content);
console.log('References added to build_eggs_all.mjs');
