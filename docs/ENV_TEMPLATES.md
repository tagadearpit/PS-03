# Copy-ready deployment environment templates

These templates contain placeholders only. Do not commit real secrets to GitHub.

## Vercel project environment variables

Add these in **Vercel → Project Settings → Environment Variables**. Apply them to Production, Preview, or both as appropriate.

```env
# Required when the Gemini API is deployed on Render.
VITE_API_BASE_URL=https://YOUR-RENDER-SERVICE.onrender.com

# Optional starter analytics values. Leave blank if analytics is not used.
VITE_ANALYTICS_ENDPOINT=
VITE_ANALYTICS_WEBSITE_ID=
```

Never add `GEMINI_API_KEY` to Vercel. Any variable beginning with `VITE_` is bundled into browser JavaScript and must be treated as public.

## Render service environment variables

Add these in **Render → Web Service → Environment**. Keep the Gemini key private.

```env
# Required: create this in Google AI Studio or your Google Cloud project.
GEMINI_API_KEY=PASTE_YOUR_SERVER_SIDE_GEMINI_KEY_HERE

# Optional; defaults to gemini-2.5-flash in render.yaml.
GEMINI_MODEL=gemini-2.5-flash

# Required: exact Vercel origin, without a trailing slash.
# Multiple origins can be comma-separated.
ALLOWED_ORIGINS=https://YOUR-PROJECT.vercel.app

# Optional.
LOG_LEVEL=INFO
```

## Build settings

| Host | Setting | Value |
| --- | --- | --- |
| Vercel | Framework | Vite |
| Vercel | Root directory | `.` |
| Vercel | Install command | `pnpm install` |
| Vercel | Build command | `pnpm build` |
| Vercel | Output directory | `dist/public` |
| Render | Runtime | Docker |
| Render | Dockerfile path | `render.Dockerfile` |
| Render | Docker build context | `.` |
| Render | Health check | `/health` |
| Render | Port | `8000` |

The repository also includes `vercel.json` and `render.yaml` with the matching settings. See `docs/DEPLOYMENT.md` for the step-by-step deployment sequence and CORS verification.
