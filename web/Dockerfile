# FanCut web: Next.js standalone server. The API's public URL is baked in at build
# time (NEXT_PUBLIC_API_URL is read by the browser), so infra passes it as a build arg.
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-alpine AS build
WORKDIR /app
ARG NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0 PORT=3000
RUN addgroup -S fancut && adduser -S fancut -G fancut
COPY --from=build --chown=fancut:fancut /app/.next/standalone ./
COPY --from=build --chown=fancut:fancut /app/.next/static ./.next/static
USER fancut
EXPOSE 3000
CMD ["node", "server.js"]
