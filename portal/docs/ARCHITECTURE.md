# Lineum Portal: Architecture Overview

This document describes the technical architecture of the Lineum Portal, its components, and infrastructure.

## 🏗 High-Level Architecture

The project is a monorepo containing three core services that form the Lineum ecosystem.

```mermaid
    User((User)) --> CF["Cloudflare (DNS & Proxy)"]
    CF --> Railway["Railway.app (Origin)"]
    
    subgraph "Railway Infrastructure"
        Railway --> Portal["Portal (SvelteKit)"]
        Railway --> Lab["Simulacrum (Lab)"]
        Railway --> API["Python API Engine"]
        Railway --> CMS["Directus CMS"]
        Portal --> AI_Agent["AI Agent (Gemini 1.5 Flash)"]
        Portal --> API
        API --> CMS
        API --> Workers["Background Generators"]
    end
```

## 🛠 Tech Stack

### 1. Frontend: Lineum Portal (Primary)
- **Framework:** [SvelteKit](https://kit.svelte.dev/)
- **Adapter:** `@sveltejs/adapter-node` (for production stability on Railway).
- **Role:** Main public-facing portal, documentation, and coordination.

### 2. Frontend: Simulakrum (Research Lab)
- **Framework:** Vite + Svelte (Standalone static service).
- **Public URL:** [simulacrum.lineum.io](https://simulacrum.lineum.io)
- **Data Engine:** WebGL/Three.js for 3D field visualization.
- **Data Source:** Audit JSON payloads (synced to the repo) from the Python engine.

### 3. Backend: API & Processing
- **Language:** Python 3.x
- **Key Components:**
  - **Lineum Core Engine:** Mathematical core for field simulations.
  - **Background Generators:** 24/7 worker processes generating the data seen in the Simulakrum.

### 4. CMS: Directus
- **Platform:** [Directus](https://directus.io/) (Headless CMS)
- **Hosting:** Dockerized on Railway.app.
- **Role:** Centralized data management and content.

### 5. AI Agent: Gemini Integration
- **Model:** Gemini 1.5 Flash (via Google AI Studio).
- **Context:** Automated build-time indexing of `/portal`, `/whitepapers`, `/hypotheses`, and core `/lineum.py`.
- **Logic:** Integrated into SvelteKit API routes with per-user and global rate limiting.
- **Role:** Interactive research assistant and portal guide.

### 6. Infrastructure & Networking
- **Platform:** [Railway.app](https://railway.app) (Monorepo deployment via `railway.json`).
- **DNS & Proxy:** Cloudflare.
  - **SSL/TLS:** **Full** mode recommended. (Use "DNS Only" temporarily to let Railway issue certificates).
  - **Proxy:** Proxied (Orange cloud) records for `lineum.io`.

## 🌿 Git Workflow & Deployment

We use a two-tier branching strategy to ensure production uptime:

- **`main` Branch:** 
  - Represents the **Live Production** state.
  - Automatic deployment to Railway is triggered on every push.
- **`dev` Branch:** 
  - Active development for new features and simulation parameters.
  - Merged into `main` only after verified stability.

### Monorepo Orchestration
Infrastructure is defined as code in [railway.json](file:///c:/Users/Tomáš/Documents/GitHub/lineum-core/railway.json), allowing Railway to simultaneously manage the Portal (port 3000) and Simulakrum (port 8080) from a single repository.

## 🔒 Security Policy
The alpha phase is strictly protected. Access requires an email address whitelisted in the Cloudflare Access dashboard. Unauthorized traffic is blocked at the edge before reaching Railway servers.

## 🎨 Design & Experience
All future portal development must adhere to the [Design & Experience Guide](file:///c:/Users/Tomáš/Documents/GitHub/lineum-core/portal/docs/DESIGN_GUIDE.md). This ensures visual consistency (glassmorphism), maintenance of the "Lineum Explorer" AI persona, and layperson-first communication standards.

## 📖 Living Document Policy
This document is a **Living Document**. To ensure the AI assistant (Antigravity) and the User are always aligned, this file MUST be updated manually or automatically whenever infrastructure components change. **Antigravity is authorized to update this file proactively as changes are executed.**

---
*Last update: February 17, 2026*
