---
description: Lineum Ethical Codex, open-source defense, and dual-use API restrictions
---

## 🛑 Lineum Ethical Codex & Dual-Usage Strategy

If the user asks about ethics, open-source strategy, dual-use technology, or restricting access to hostile entities (e.g., weapons manufacturers, mass surveillance, or specific states), **DO NOT propose creating a new ethical manifesto**. The project already has a robust ethical framework in place.

**The single source of truth is:** `docs/LINEUM_CODEX_v1.md` (and its translations in `portal/src/lib/data/docs/`).

### How the defense strategy works:
1. **The Science is Open (Cypherpunk/MAD Doctrine):** The mathematical core and the Lineum equation are released as open-science under the AGPLv3 license out of principle, ensuring no single state or corporation can monopolize it. This mathematically "arms" everyone equally and removes the exclusive threat vector from the creators. 
2. **The API is Sovereign:** The commercial infrastructure (Portál Lineum / API keys / enterprise SaaS hosting) is solely under the team's control.
3. **Hard Stop API Restrictions:** The Codex explicitly defines "C) Tvrdé Zastavení" (Hard Stop) rules. The Lineum API will never serve:
   - Lethal/Weapons targeting and the "kill chain".
   - Repressive mass surveillance.
   - Unauthorized infrastructure attacks.
   - Maximalization of suffering/destruction.

**What the AI must do:**
- Always refer back to `docs/LINEUM_CODEX_v1.md` when ethics or access control is mentioned.
- Remind the user that the strategy is already encoded in the Codex and enforceable at the software layer via the Kill Switch for API users.
- Never write new ethics documents, as the `v1` Codex is the designated master anchor.
