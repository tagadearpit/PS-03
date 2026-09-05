# PayGuard AI analysis API contract

The frontend expects a stateless `POST /api/v1/analyze` operation. A deployed service may accept either `application/json` or `multipart/form-data`.

## JSON request

```json
{
  "input_type": "text | url | camera",
  "content": "The raw SMS, URL, or decoded QR payload",
  "source": "manual | interceptor"
}
```

For an image upload, send a multipart field named `file` and include `input_type=image`. The service may run OCR and QR extraction before scoring.

## Response

```json
{
  "score": 18,
  "severity": "safe",
  "label": "Looks safe",
  "summary": "No meaningful scam signals found.",
  "action": "Safe to continue",
  "action_detail": "Always verify the merchant name before approving a payment.",
  "source": "Payment QR",
  "entity": "Blue Tokai Coffee",
  "threats": [
    {
      "title": "Verified VPA format",
      "detail": "The payment handle follows a standard UPI pattern.",
      "severity": "safe"
    }
  ],
  "timestamp": "2026-09-04T05:57:50Z",
  "trace_id": "A1B2C3D4"
}
```

`score` is an integer from 0 to 100. `severity` must be one of `safe`, `suspicious`, or `high`. The service should not persist submitted messages, images, URLs, or QR payloads.

## Integration notes

The Vite client can use `import.meta.env.VITE_API_BASE_URL` as the service origin. Keep the API host in deployment configuration rather than hardcoding a production URL. The simulator uses `source=interceptor` so a future Android notification listener or webhook can be represented separately from manual analyst checks.
