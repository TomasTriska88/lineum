# Lineum Core

> **Emergence of stable localized excitations in discrete fields without physical constants.**

Lineum is an open research project investigating whether particle-like structures ("linons") and field-mediated interactions can arise from simple, local update rules on a discrete grid, without embedding any physical laws or constants a priori.

## 📂 Project Structure

This monorepo contains three distinct components:

| Component | Path | Description | Tech Stack |
| :--- | :--- | :--- | :--- |
| **Core** | `/` | The simulation engine and audit tools. | Python 3.11 |
| **Portal** | `/portal` | Official web interface and knowledge base. | SvelteKit (Node) |
| **Lab** | `/lab` | "Simulacrum" - Interactive 3D visualizer. | Svelte/Vite |

---

## 🔬 Core (Simulation Engine)
The heart of the project. A Python-based engine that runs the discrete field updates.

*   **Entry Point**: `lineum.py`
*   **Documentation**: `whitepapers/lineum-core.md` (Scientific paper)
*   **Usage**:
    ```bash
    # Run a simulation
    python lineum.py
    ```
*   **Audit**: See `whitepapers/` for full scientific methodology and reproduction steps.

---

## 🌐 Portal (Web Interface)
The public face of Lineum ([lineum.io](https://lineum.io)). It serves as:
1.  **Wiki**: Hosting the whitepapers and documentation.
2.  **Context**: Explaining the mission and finding linons.
3.  **Lina**: An AI assistant with full context of the project.

*   **Deployment**: Deployed to Railway from `main`.
*   **Safety**: Uses `npm run safe-merge` to ensure quality.

---

## 🧪 Lab (Simulacrum)
An interactive 3D laboratory for visualizing field data and harmonics.

*   **Status**: Experimental / Visualizer.
*   **Tech**: Three.js + Svelte.
*   **Deployment**: Deployed to Railway as a static site.

---

## 🚀 Deployment & Workflow

### Git Protocol
*   **`dev` branch**: All development happens here.
*   **`main` branch**: Production releases only.

### How to Deploy (Portal)
We use a **Safe Merge** protocol to prevent broken builds in production.
```bash
cd portal
npm run safe-merge
```
This script runs tests, builds the site, checks for i18n issues, and only then merges `dev` into `main` and pushes.

---

## 📜 License
*   **Code**: MIT License.
*   **Whitepapers**: CC BY 4.0.
