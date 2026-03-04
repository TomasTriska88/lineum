# Lineum™

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
*   **Audit**: See `whitepapers/` for full scientific methodology or [Verification Checklist](docs/verification_checklist.md) for independent reproduction.

### ⚡ Hardware Acceleration (CUDA/GPU)
Lineum Core runs on standard CPU (NumPy) by default and does **not** force heavy GPU dependencies in `requirements.txt`.
However, for massive scientific grid runs, reference pack generations, or local testing, you can seamlessly unlock **10x-30x speedups** if you have an Nvidia GPU:
1. Install PyTorch with CUDA support locally: `pip install torch --index-url https://download.pytorch.org/whl/cu121`
2. The core physics engine (`lineum_core/math.py`) will **auto-detect** the GPU and automatically route tensor calculations through hardware CUDA cores.

### 📦 Reference Pack
For independent offline verification without reproducing the entire run, download the pre-built reference pack from the [GitHub Releases](https://github.com/TomasTriska88/lineum-private/releases) page (attached as an asset to `v*` tags).

To verify the downloaded pack:
```bash
python scripts/verify_reference_pack.py --pack <path_to_downloaded_zip>
```

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

## 🛠 Troubleshooting
### Localhost vs 127.0.0.1 (Windows IPv6 Bug)
SvelteKit (Vite) development servers on Windows frequently bind to the IPv6 loopback (`::1`) while browsers attempt to resolve `localhost` via IPv4. This results in standard `npm run dev` endpoints returning a **404 error** or `ERR_CONNECTION_REFUSED`.
To bypass this, always run the dev servers bound explicitly to IPv4 via `--host` and navigate to the numeric IP:
```bash
# Portal
npx vite dev --host 127.0.0.1 --port 5173

# Lab
npx vite dev --host 127.0.0.1 --port 5174
```
**Do not use `localhost`** in the browser in these cases, always use `http://127.0.0.1:5173` explicitly.

---

## 👥 Team & Acknowledgements
* **Tomáš Tříska**: Primary author, lead researcher, and creator of the Lineum Core engine.
* **Kateřina Marečková**: Contributor. Provided foundational critical opposition, hypothesis testing, and conceptual clarity for the ontological frameworks.
* **Vlastimil Smeták**: Contributor. Contributed key insights and correlations with the external OEA (Obecně Evoluční Algoritmus) model, influencing structural hypotheses.

---

## 📜 AGPLv3 + Commercial License

This entire repository (including the core engine and `/portal`) is open-source and natively governed by the **GNU AGPLv3 License**. 
If you operate Lineum as a network service (SaaS) and modify the codebase, you must offer the source code of your running version to the users of your service. 

If you wish to operate Lineum in a closed-source ecosystem or cannot comply with the AGPLv3 requirements, a **Commercial License / Exception** is available from the copyright holder.

Contact for commercial licensing: TODO_CONTACT

### 🛡️ Trademarks
"Lineum™" and "Lina™" are trademarks of Tomáš Tříska.
Explicit permission is granted to contributors and users of the AGPLv3 Core Engine to use the "Lineum" and "Lina" names in connection with the project, including the Portal and Lab interfaces, as long as such use is non-commercial (in accordance with the Codex) and accurately refers to this original repository.
