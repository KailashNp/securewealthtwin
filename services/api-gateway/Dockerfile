FROM node:20-alpine

WORKDIR /app

# Install dependencies first (layer cache optimization)
COPY package*.json ./
RUN npm install --omit=dev

# Copy source
COPY . .

# Gateway runs on port 8000
EXPOSE 8000

CMD ["node", "index.js"]
