# Lineum Merch: Equation Edition

This directory contains the final artwork and mockups for the "Equation" merchandise edition.

## Generation Prompts

### 1. Base Art (`art.png`)
**Prompt:**
> Raw printable graphic asset. A minimalist typographic and mathematical design on a PURE SOLID BLACK BACKGROUND (#000000). NO GRADIENTS OR NOISE IN THE BACKGROUND. IT MUST BE TRUE BLACK.

> The design features a sleek, futuristic high-tech equation: '∂ₜψ = ∇²ψ + φ ψ + ∇φ'. 
> CRITICAL CHECK: There MUST be exactly three 'ψ' symbols and exactly two 'φ' symbols. Do not erase the 'ψ' next to the middle 'φ'.
>
> CRITICAL COLOR INSTRUCTIONS:
> - The math operators (∂, ₜ, =, +, ∇, ²) MUST be pure WHITE.
> - Every single instance of the letter 'ψ' (psi) MUST be vibrant CYBER-CYAN. 
> - Every single instance of the letter 'φ' (phi) MUST be vibrant PURPLE/FUCHSIA. 
> - Look at the middle term: 'φ ψ'. The first symbol 'φ' MUST be PURPLE. The second symbol 'ψ' MUST be CYAN.
> 
> The equation should use a coding font similar to 'JetBrains Mono'. Below the equation, perfectly centered, make the text 'lineum.io' relatively small, sleek, and elegant using a sans-serif font like 'Inter'. The text 'lineum.io' should have a cyber-cyan to fuchsia/purple gradient. Flat 2D vector style.

**Post-Processing:**
AI models cannot generate perfect native alpha channels. Generate the image on a pure black background as instructed above, and then use the mathematical *Un-premultiply* script preserved in the repository to extract the true semi-transparent edges.
Run: `node ../scripts/process_alpha.mjs ../equation/art.png`

## Spreadshop Product Strategy

To maintain a premium, "geek-chic", Dark Mode aesthetic suitable for a high-end tech/cyber ecosystem, strictly adhere to these product curation and design placement rules:

### 1. Color Palette
- **Rule:** Deep Dark Colors. The neon cyber-cyan and fuchsia elements must pop against the darkness. For each specific product, curate and select **only one** best-fitting color (either Pitch Black OR Deep Navy Blue).
- **Goal:** Maintain an exclusive "dark mode" aesthetic while allowing flexibility to pick the dark shade that best highlights the product's material. Avoid giving users multiple color choices on the same item.
- **Banned:** White, grey, bright colors, heather colors, and any non-dark variations.

### 2. Design Placement
- The `equation` graphic should be placed as a single, large horizontal print **centered on the front chest** (around 70%+ width).
- **Banned Placements:** Do NOT place the design on the back. Do not place it as a tiny "pocket logo".

### 3. Apparel Curation
- **Focus:** Premium organic, minimalist shapes (e.g., Stanley/Stella Creator, Cruiser, long sleeves, boxy fits, hoodie dresses).
- **Exceptions:** Simple dark winter beanies (Jersey Beanie, Patch Beanie) are permitted.
- **Banned Apparel Categories:**
  - Anything with a front zipper or button placket that splits the chest design (Zip-Up Hoodies, Jackets, Polos, Work Shirts, Softshells, Sherpas).
  - V-Necks (interferes with horizontal placement).
  - Sportswear & activewear (Gildan, JAKO, CRAFT, gym shorts, sweatpants, swim trunks, leggings).
  - Caps and Hats (Snapback, Trucker, Baseball, Bucket Hats, Santa Hats). The equation graphic is too wide for curved caps and loses detail.
  - Aprons (Cooking, Artisan, Children's). Breaks the premium cyber-tech aesthetic.
  - **Kids & Babies:** The brand aesthetic is strictly adult/professional techwear. All kids' sizes and infant clothing must be deactivated.

### 4. Accessories Curation
- **Focus:** Items that fit on a developer's desk, an urban commuter's back, or terminal setup. 
  - Full Colour Black Mugs & Panoramic Full Colour Mugs.
  - Heavyweight Recycled Tote Bags & Shoppers.
  - Technical bags: Roll Top Backpacks, Messenger/Shoulder Bags, dark Premium Hip Bags/Bumbags.
  - Laptop sleeves/bags (13" & 15") and Canvas zip/pencil pouches.
  - Dark Sofa Pillows/Pillowcases (Black/Navy) for office/dev-cave aesthetics.
  - Dark/Matte Metallic Insulated Water Bottles (e.g., Panoramic Insulated Water Bottle in Navy/Black).
- **Banned Accessory Categories:** 
  - Standard white/contrast mugs, beer mugs, camper mugs.
  - Coasters, lunchboxes.
  - Drawstring gymsacs, mesh shopping bags, retro bags, standard school backpacks.
  - White or brightly colored bottles, metallic glitter bottles, cookie jars, bottles with straws.
  - Buttons/Pins. The graphic requires a dark background and too much small detail is lost on small white pins.
  - **No Baked-in Backgrounds:** We do not add artificial dark backgrounds/rectangles to our transparent neon graphic just to make it visible on white/bright products. We skip those products entirely.
