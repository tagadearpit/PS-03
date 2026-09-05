# PayGuard AI deployment guide

## 1. Deploy the frontend to Vercel

Import the GitHub repository into Vercel. Use these settings:

| Setting | Value |
| --- | --- |
| Framework preset | Vite |
| Root directory | `.` |
| Install command | `pnpm install` |
| Build command | `pnpm build` |
| Output directory | `dist/public` |
| Node.js version | 20 or newer |

Add this Vercel environment variable:

| Variable | Value |
| --- | --- |
| `VITE_API_BASE_URL` | The deployed Render API URL, for example `https://payguard-ai-api.onrender.com` |

The `VITE_` prefix is required because this value is used by the browser. Do not add `GEMINI_API_KEY` to Vercel. It must remain server-side on Render.

## 2. Deploy the Gemini backend to Render

Create a new Render Web Service connected to the same repository. Use these settings:

| Setting | Value |
| --- | --- |
| Runtime | Docker |
| Dockerfile path | `render.Dockerfile` |
| Docker build context | `.` |
| Health check path | `/health` |
| Port | `8000` (the Dockerfile exposes it) |
| Plan | Any plan appropriate for your traffic; the free instance may sleep when idle |

Add these Render environment variables:

| Variable | Required | Value |
| --- | --- | --- |
| `GEMINI_API_KEY` | Yes | Your Google Gemini API key. Keep this secret. |
| `GEMINI_MODEL` | No | `gemini-2.5-flash` (default) |
| `ALLOWED_ORIGINS` | Yes | Your Vercel origin, for example `https://payguard-ai.vercel.app`; separate multiple origins with commas. |
| `LOG_LEVEL` | No | `INFO` |

The backend uses `google-genai` structured output and calls Gemini for every manual submission to `/api/v1/analyze`: image uploads, SMS/text, URLs, and camera submissions. Requests are processed in memory and are not written to a database.

When entering these values manually in Render, type only `render.Dockerfile` in **Dockerfile Path** and only `.` in **Docker Build Context**. Do not type the explanatory words `repository root` into either field. Leave **Root Directory** blank unless Render requires it; if a root directory is required, use `/` or `.` according to the Render UI.

## 3. Verify the connection

After both services are deployed, open the Vercel site and submit a text or URL in Verification Studio. The browser should receive a structured response from Render. Confirm the Render logs contain the stages `INGESTION`, `VISION_OCR` where applicable, `LINK_ANALYSIS` for links, `SEMANTIC_EVAL`, and `RISK_ENGINE` with an eight-character trace ID.

If the browser shows a CORS error, update `ALLOWED_ORIGINS` on Render to exactly match the Vercel origin, redeploy the Render service, and retry. If the response says Gemini is not configured, add `GEMINI_API_KEY` to Render and redeploy.

## 4. GitHub commands

```bash
git add .
git commit -m "Add Gemini backend and deployment configuration"
git push origin main
```
