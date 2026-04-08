FROM node:18-alpine AS builder

WORKDIR /web

COPY clue_ui_sandbox/frontend/package*.json ./
RUN npm config set registry https://registry.npmmirror.com && npm install

COPY clue_ui_sandbox/frontend/ ./
RUN npm run build

FROM nginx:1.27-alpine

COPY --from=builder /web/dist /usr/share/nginx/html
COPY clue_ui_sandbox/deploy/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

