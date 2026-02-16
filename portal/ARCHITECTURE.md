# Lineum Portal: Architecture Overview

This document describes the technical architecture of the Lineum Portal, its components, and infrastructure.

## 🏗 High-Level Architecture

The project is divided into three main layers that together form the Lineum ecosystem.

```mermaid
graph TD
    User((User)) --> CF[Cloudflare DNS / Proxy]
    CF --> Frontend[SvelteKit Frontend / Portal]
    Frontend --> API[Python API Engine]
    Frontend --> CMS[Directus CMS]
    API --> CMS
    API --> DB[(DB / Data Storage)]
    API --> Workers[Background Generators]
    
    subgraph "Infrastructure (Railway.app)"
        Frontend
        API
        CMS
        Workers
    end
```

## 🛠 Tech Stack

### 1. Frontend: Lineum Portal & Lab
- **Framework:** [SvelteKit](https://kit.svelte.dev/)
- **Language:** TypeScript
- **Key Features:**
  - **Portal:** Main entry point, documentation, and presentation.
  - **Lab:** Interactive laboratory environment for simulations and analysis (utilizes Three.js and Chart.js).
- **Deployment:** Automated build on Railway.app on every push to `main`.

### 2. Backend: API & Processing
- **Language:** Python 3.x
- **Key Components:**
  - **Lineum Core Engine:** The mathematical and simulation core of the project.
  - **FastAPI / Flask:** (Planned) To serve the paid API.
  - **Background Generators:** Continuous 24/7 processes generating data for simulations and the API.

### 3. CMS & Data Management: Directus
- **Platform:** [Directus](https://directus.io/) (Headless CMS)
- **Role:** Centralized data management, content for the Portal, and administrative interface for simulations.
- **Hosting:** Self-hosted on Railway.app (Docker-based).

### 4. Infrastructure (Hosting)
- **Platform:** [Railway.app](https://railway.app)
  - **Model:** PaaS (Platform as a Service) – zero server management.
  - **Scaling:** Usage-based (billing based on actual CPU and RAM consumption).
- **DNS & Domain:** [Cloudflare](https://www.cloudflare.com/)
  - **Domain:** `lineum.io`
  - **Security:** SSL, DDoS protection, and speed optimization via Cloudflare Proxy.

## 🚀 Automation & Deployment

Deployment is handled collaboratively via **GitHub Actions**:
- **Verification:** Every change undergoes testing.
- **Approval:** Production deployment can require manual confirmation by the user.
- **Transparency:** Infrastructure configuration is stored as code (`railway.json` / workflow files).

## 📖 Living Document Policy

This document is a **Living Document**. It MUST be updated whenever:
- New infrastructure components are added or modified.
- Deployment automation (CI/CD) workflows are established or changed.
- Domain or security settings (DNS, SSL, Cloudflare) are updated.
- Significant architectural shifts occur in the Portal or Lab.

Both the user and the AI assistant are responsible for keeping this overview in sync with the actual state of the repository.

---
*Last update: February 16, 2026*
