# LINEUM LAB UX CANON

**MANDATORY DESIGN RULE FOR THE ENTIRE LAB**  
*This is the single official standard. All future screens and changes must adhere to this.*

## 1. LAB MUST BE SELF-EXPLANATORY (NO HUMAN EXPLANATION REQUIRED)
Anyone opening the Lab for the first time must understand within 10 seconds:
- what it is
- what it isn't
- what they are looking at
- whether it passed
- what to click next

## 2. "Explain Pack" is a Mandatory Contract
Every Lab scenario (Core Validation, Reality Alignment, Playground) MUST return an `explain_pack` from the backend (Validation Core) containing:
- `one_liner_human`: 1 sentence for a layman
- `what_you_see`: 2–4 ultra-simple bullet points (e.g., "Bright=more, Dark=less")
- `what_it_is_not`: 2 bullet points (e.g., "NOT multi-electron chemistry")
- `success_criteria_human`: 1 sentence explaining what PASS means
- `next_action_pass`: 1 sentence + CTA label
- `next_action_fail`: 1 sentence + CTA label
- `disclaimers`: Automatically generated based on scenario (2D/units/periodic/single-particle/soft potential...)
- `glossary_terms_used`: List of terms appearing on the page.

**The frontend MUST NOT contain hardcoded explanatory texts.** It strictly renders the Explain Pack to prevent contradictions.

## 3. Standard Page Skeleton (Always the same)
After a RUN, the layout must follow this exact top-to-bottom sequence:
1. **"How to use this Lab" mini-panel** (Always visible, 4 steps)
2. **Verdict block** (PASS/FAIL + checklist expectations) + **"Next action"** (ONE primary CTA button)
3. **What you're seeing** & **What this is NOT** (From Explain Pack)
4. **Quick Visual** (1 main window: either a map or a chart)
5. **Scientific Details** (Collapsible) — All other maps, charts, raw JSON, and diffs.
6. **Run Manifest / Export / Compare** (Accessible but not overwhelming).

## 4. Layman-Friendly Mode: "Particle View" vs "Scientific View"
- Toggle available wherever a density map is shown.
- **Particle View**: Visualization render over the *same* data (halo/contours/pseudo-3D).
- **Scientific View**: Mathematical `log|psi|^2` / `phase` / `V(r)`.
- **Both are true** (same underlying data), just different renders.

## 5. Glossary is integrated, not external
- Accessible with 1 click anywhere in the Lab.
- Defines terms ultra-simply: "Cloud", "Ground state", "p-state", "Leak", "Validate", "Explore".
- Fully consistent with the Explain Pack.

## 6. VALIDATE Must Be Foolproof
- VALIDATE presets typically PASS on the first run (default safe configs).
- Auto-Fix is a rescue mechanism, not the standard workflow.
- Auto-Fix must be **ONE** button ("Make stable") that performs multi-step stabilization (dt↓, eps↑, recommend grid↑) without requiring repeated clicks.
- If it cannot stabilize, the UI clearly states "Needs larger grid" and offers a 1-click application.

## 7. Presets: Less is More
- Do not fill the UI with the periodic table.
- Keep H/He/C/O as milestones (Z=1, 2, 6, 8).
- Include distinct "Shape Presets":
  - `p-state` (two lobes)
  - `double-well` (two blobs)
  - `ring potential` (ring)

## 8. Charts Must Be Charts
- All time-series metrics must use `<InteractiveChart>` (Chart.js + tooltip/zoom).
- Base64 images are permitted ONLY for heatmaps/fields.

## 9. TESTS-ALWAYS POLICY (Automatic, Implicit)
- Every code change, text edit, preset update, expectation modification, or UI behavior tweak requires corresponding tests.
- Tests are written automatically as part of the change, not upon request.
- PRs are blocked until tests are added/updated and green.

## 10. Enforcement
- Lint/Test must fail the build if a scenario lacks an Explain Pack or mandatory keys.
- Lint/Test must fail if time-series are returned as base64 images.
- Golden CI must strictly enforce `overall_pass` and full `expectation_results`.
