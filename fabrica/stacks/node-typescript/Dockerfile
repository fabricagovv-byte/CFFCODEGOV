FROM node:22-alpine
WORKDIR /app
COPY src ./src
COPY package.json .
USER node
EXPOSE 8000
CMD ["node", "--experimental-strip-types", "src/server.ts"]
