# PayGuard AI

PayGuard AI is a warm, executive-style verification studio for checking UPI payment requests, suspicious messages, URLs, and QR codes before a user taps. The repository includes a Vercel-ready frontend and an independent, stateless FastAPI service for Gemini analysis on Render.

## What is included

- A responsive analyst dashboard built with React, TypeScript, Tailwind CSS, and Vite.
- Four verification modes: image / QR upload, SMS or WhatsApp text, URL inspection, and live camera preview.
- Animated 0–100 risk meter with safe, review, and high-risk states.
- Signal breakdown cards with plain-English threat explanations and recommended actions.
- Live System Monitor simulator for demonstrating background SMS and QR interception flows.
- Recent activity table, keyboard-accessible controls, mobile navigation, reduced-motion support, and toast feedback.
- Email/password login and account-creation pages with protected studio and history routes.
- Dedicated auth artwork for login and signup, plus a clearer left-to-right architecture visual.
- Warm English cream design system with Playfair Display, DM Sans, and DM Mono typography.
- FastAPI backend in `backend/` with Gemini structured output, OCR/QR dependencies, CORS, health checks, and trace logging.

## Run locally

Requirements: Node.js 20+, pnpm 10+, and Git.

```bash
pnpm install
pnpm dev
```

Open the local Vite URL printed in the terminal. Before committing changes, run:

```bash
pnpm check
pnpm build
```

To preview the production build locally:

```bash
pnpm start
```

To run the Gemini backend locally:

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY=your_key
export ALLOWED_ORIGINS=http://localhost:3000
uvicorn app.main:app --reload --port 8000
```

## Environment and API connection

When the backend is running, every manual submission in Verification Studio calls `POST /api/v1/analyze`: image, SMS/text, URL, and live-camera submissions. The current preview falls back to deterministic demo data only when the backend is unreachable. For deployment, configure `VITE_API_BASE_URL` in Vercel to point at the Render service. Backend-only variables such as `GEMINI_API_KEY`, `ALLOWED_ORIGINS`, and `LOG_LEVEL` must stay on Render and must never be exposed to the Vite client. See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md), [`docs/ENVIRONMENT.md`](docs/ENVIRONMENT.md), [`docs/ENV_TEMPLATES.md`](docs/ENV_TEMPLATES.md), and [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md).

Authentication routes are `/login` and `/signup`. The current account flow is a browser-local demo session intended for UI validation; replace it with a production identity provider before launch. See [`docs/AUTHENTICATION.md`](docs/AUTHENTICATION.md).

## Deployment

For Vercel, import the repository and use `pnpm build` as the build command with `dist/public` as the output directory. The included `vercel.json` already contains the matching build and SPA fallback configuration.

The included FastAPI analysis service deploys on Render with `backend/Dockerfile`. It calls Gemini on every request, returns structured risk data, and does not persist submitted inputs. Full Vercel and Render settings are in [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

## Push this project to GitHub

Create an empty repository on GitHub, then run these commands from the extracted project folder. Replace the URL with your repository URL:

```bash
git init
git add .
git commit -m "Build PayGuard AI verification studio"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

If the repository already has a remote configured, use `git remote -v` to inspect it and then run `git push -u origin main` after committing.

## Design direction

PayGuard uses a soft cream canvas (`#FAF7F2`), linen-white cards, deep charcoal typography, and aged amber as the action color. Motion is deliberately short and functional: staggered entrance, gauge count-up, button feedback, and a slide-in simulator drawer. No data is persisted by the frontend.

## Verification

The final project passes TypeScript checks and the production build. Desktop and mobile previews were visually reviewed. The fake electricity bill simulator was tested end-to-end: it updates the score to 94, switches the status to High risk, shows a blocking recommendation, changes the signal breakdown, increments activity, and displays a toast notification.

## License

MIT
