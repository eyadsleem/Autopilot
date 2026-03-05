# Frontend stub

This repository includes a **dependency-free frontend stub** so `npm install` succeeds in restricted/proxied CI environments.

The previously scaffolded Next.js files remain in `frontend/app/*` as reference UI templates, but package dependencies are intentionally omitted here.

## Commands

```bash
cd frontend
npm install
npm run dev
```

When network access to npm is available, you can restore the Next.js stack by adding `next`, `react`, `react-dom`, and `next-auth` dependencies back to `package.json`.
