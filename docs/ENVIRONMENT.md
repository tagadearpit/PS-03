# Environment variables

For a deployed frontend, configure these values in the hosting provider rather than committing secrets:

| Variable | Required | Purpose |
| --- | --- | --- |
| `VITE_API_BASE_URL` | Optional in preview | Origin for the stateless `POST /api/v1/analyze` service. |
| `VITE_ANALYTICS_ENDPOINT` | Optional | Analytics script origin from the starter workspace. |
| `VITE_ANALYTICS_WEBSITE_ID` | Optional | Analytics website identifier from the starter workspace. |
| `GEMINI_API_KEY` | Backend only | Server-side key for a future semantic analysis service; never expose it to the Vite client. |
| `ALLOWED_ORIGINS` | Backend only | Comma-separated origins allowed to call the analysis service. |
| `LOG_LEVEL` | Backend only | Python service logging level, such as `INFO`. |

The local preview uses deterministic demo data and does not require any of these values.
