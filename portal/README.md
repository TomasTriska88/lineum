# sv

> [!IMPORTANT]
> **Git Protocol:**  
> 1. All development **MUST** happen on the `dev` branch.  
> 2. The `main` branch is reserved for **production releases only**.  
> 3. Never commit directly to `main`. Merge `dev` -> `main` only when ready to deploy.

Everything you need to build a Svelte project, powered by [`sv`](https://github.com/sveltejs/cli).

## Creating a project

If you're seeing this, you've probably already done this step. Congrats!

```sh
# create a new project
npx sv create my-app
```

To recreate this project with the same configuration:

```sh
# recreate this project
npx sv create --template minimal --types ts --no-install portal
```

## Developing

Once you've created a project and installed dependencies with `npm install` (or `pnpm install` or `yarn`), start a development server:

```sh
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

## Building

To create a production version of your app:

```sh
npm run build
```

- Build the project: `npm run build`
- Preview the build: `npm run preview`

---

## 🛠 Task Tracking & Roadmap

> [!IMPORTANT]  
> Podle protokolu **Dual Context Check** jsou tyto lokální úkoly sledovány synchronně s hlavní [todo.md](file:///c:/Users/Tomáš/Documents/GitHub/lineum-core/todo.md) v kořeni projektu.

### Aktuální technické úkoly
- [ ] Refaktorovat `FieldShader.svelte` pro lepší výkon na mobilních zařízeních.
- [ ] Implementovat Skeleton UI pro načítání auditních dat.
- [ ] Přidat interaktivní tutoriál pro laiky (§4.1).

> To deploy your app, you may need to install an [adapter](https://svelte.dev/docs/kit/adapters) for your target environment.
