# Infrastructure

FanCut runs on **Azure Container Apps**: one app for the API, one for the web, in a
single environment, with a container registry, Log Analytics and **Application
Insights**. Everything is declared in Bicep and deployed with the Azure Developer CLI.

| File | What it does |
|---|---|
| [`main.bicep`](main.bicep) | Subscription scope: the resource group and the outputs azd reads back |
| [`resources.bicep`](resources.bicep) | The registry, managed identity, environment, both apps, monitoring |
| [`main.parameters.json`](main.parameters.json) | Maps azd environment variables to Bicep parameters |
| [`../azure.yaml`](../azure.yaml) | Tells azd which folders are services and how to build them |

## What is wired automatically

The two hostnames only exist once Azure creates the apps, so Bicep derives them from
the app names and the environment's domain and passes them where they are needed:

- `NK_MCP_ALLOWED_HOSTS` = the API's own hostname, so `/mcp` accepts requests.
- `NK_CORS_ORIGINS` = the web app's URL, so browsers may call the API from it.
- `NEXT_PUBLIC_API_URL` = the API's URL, baked into the web image at build time
  (`azd deploy` passes the `API_URL` output as a Docker build argument).
- `APPLICATIONINSIGHTS_CONNECTION_STRING` for the API, so every agent call is traced.

Keys (Foundry, Speech) are **Container Apps secrets**, never environment variables in
plain text, and never in the repository. The apps pull images with a user-assigned
managed identity (AcrPull); the registry's admin user is off. The API runs as one
always-on replica because a channel lives in memory for the length of its stream.

## Deploy (one time, about ten minutes)

Prerequisites: [Azure Developer CLI](https://aka.ms/azd-install), Docker running, an
Azure subscription, and the Foundry resource created in the portal (its endpoint,
deployment name and key; the same key and region serve Azure AI Speech).

```bash
azd auth login
azd init -e fancut            # new environment named "fancut"; pick the subscription and region

# The model and voice keys. Empty values are allowed: the API then speaks its
# deterministic templates and hides the voice switch.
azd env set NK_LLM_ENDPOINT   https://<resource>.openai.azure.com/
azd env set NK_LLM_DEPLOYMENT gpt-4.1-mini-1
azd env set NK_LLM_API_KEY    <key>
azd env set NK_SPEECH_REGION  westus3
azd env set NK_SPEECH_KEY     <key>

azd up                        # provisions infra/, builds both images, deploys them
```

`azd up` prints the two URLs at the end. They are also in `azd env get-values` as
`WEB_URL` and `API_URL`.

## Verify on the live hostnames

```bash
API=$(azd env get-value API_URL)
WEB=$(azd env get-value WEB_URL)

# 1. Health: the API is up, and says whether the model and Speech are configured.
curl -s "$API/health"

# 2. MCP: the handshake succeeds on the API's own hostname.
curl -s -X POST "$API/mcp/" \
  -H "Accept: application/json, text/event-stream" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"check","version":"0"}}}'

# 3. CORS: a preflight from the web app's origin is allowed...
curl -s -i -X OPTIONS "$API/channels" -H "Origin: $WEB" \
  -H "Access-Control-Request-Method: POST" | grep -i access-control-allow-origin

# ...and one from an unknown origin is not (no allow-origin header comes back).
curl -s -i -X OPTIONS "$API/channels" -H "Origin: https://example.com" \
  -H "Access-Control-Request-Method: POST" | grep -i access-control-allow-origin
```

Then open `$WEB` on a laptop and a phone and watch a channel to full time.

## Day to day

```bash
azd deploy            # ship code changes (both services)
azd deploy api        # or just one
azd monitor --logs    # Application Insights
azd down              # delete everything when the demo period ends
```

Costs: two small Container Apps, a Basic registry and Log Analytics at 30 days'
retention. The Foundry model and Speech are billed by use on the existing resource.
