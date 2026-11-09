# Step 1: install packages and build the app
FROM node:22-slim AS build
WORKDIR /app

# Install the packages first, so this slow step is cached
# until package-lock.json changes.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# The browser calls the backend at this address. Next.js puts it into the
# page code at build time, so it is set here and not when the container runs.
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Step 2: a small image with only what is needed to run the built app
FROM node:22-slim
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    HOSTNAME=0.0.0.0 \
    PORT=3000

# "standalone" output is a ready-to-run server with only the packages it uses
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static

# Run as the normal "node" user, not root
USER node
EXPOSE 3000
CMD ["node", "server.js"]
