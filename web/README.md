# FanCut Web

Next.js 16 (App Router), React 19, TypeScript (strict), Tailwind CSS v4, Motion.

```bash
npm ci              # install
npm run dev         # http://localhost:3000 (expects the API on http://127.0.0.1:8000)
npm run lint && npm run typecheck && npm test && npm run build   # quality gates
npm run tokens      # regenerate src/app/tokens.css from src/design/tokens.ts
```

| Route | What it is |
|---|---|
| `/` | Landing: start a channel, watch the two demo fans |
| `/start` | Onboarding: describe yourself in plain language, read it back, start |
| `/channel?profile=arjun&lang=hi&speed=30` | One fan's channel; `profile` is `arjun`, `maya` or a compiled profile id |
| `/split?a=arjun&b=maya` | Two fans, one matchday, side by side |
| `/studio?profile=arjun` | Studio and Trust: audit trail, overlay inspector, measurements |
| `/design` | The design system gallery |

`NEXT_PUBLIC_API_URL` points the browser at the API (default `http://127.0.0.1:8000`); in
Azure it is baked into the image at build time by `infra/`.
