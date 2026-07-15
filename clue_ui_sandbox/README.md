# clue_ui_sandbox 开发与部署文档

## 1. 项目结构

- `backend/`：FastAPI 后端
- `frontend/`：Vue3 + Vite + Element Plus 前端
- `deploy/`：Docker 部署文件（`docker-compose.yml`、`backend.env`、`nginx.conf`）

本系统为独立项目，不依赖仓库其他模块导入。

## 2. 固定数据源

- SQLite：`pic/database/wupin_tanwei_dabt.db`
- 表：`results`
- 主键：`id`
- 图片字段：`图片路径`（HTTP URL，前端直接展示）

## 3. 关键接口

- `GET /api/clues`
- `GET /api/clues/{id}`
- `POST /api/clues/{id}/commit`
- `GET /api/stats/summary`
- `GET /api/stats/by-violation`
- `GET /api/stats/by-location`
- `GET /api/stats/trend-by-violation`
- `GET /healthz`

## 4. 提交模式

- `CLUE_COMMIT_GATEWAY=mock`：仅更新本地 `is_committed=1`
- `CLUE_COMMIT_GATEWAY=dm`：通过 `dmPython` 写入太极数据库

太极库相关配置在 `deploy/backend.env` 中维护。

## 5. 本地开发启动

### 5.1 后端

```powershell
cd clue_ui_sandbox/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5.2 前端

```powershell
cd clue_ui_sandbox/frontend
npm install
npm run dev
```

## 6. Docker 部署

当前对外端口：

- 前端：`6586`
- 后端：`6587`

健康检查地址：

- `http://<服务器IP>:6587/healthz`

### 6.1 镜像模式（生产推荐）

在仓库根目录构建镜像：

```bash
docker build -t clue-backend:1.0.0 -f clue_ui_sandbox/backend/Dockerfile .
docker build -t clue-frontend:1.0.0 -f clue_ui_sandbox/frontend/Dockerfile .
```
打包：
```bash
docker save -o clue-ui-images-1.0.0.tar clue-backend:1.0.0 clue-frontend:1.0.0
```
加载镜像文件：
```bash
# 加载镜像文件
docker load -i clue-ui-images-1.0.0.tar
# 或者使用
docker load < clue-ui-images-1.0.0.tar
```
启动：

```bash
cd clue_ui_sandbox/deploy
docker compose up -d
```

### 6.2 代码挂载模式（后端快速改代码）

你已使用如下挂载方式让后端直接读取宿主机代码：

- `/data1/qwen2v/road_property_rightsmodel/clue_ui_sandbox/backend/app:/app/app`

这样修改后端代码后，不需要重建镜像；通常只需重建后端容器（见第 7 节）。

### 6.3 前端更新说明（重点）

当前前端容器是 `Nginx + 静态文件` 模式，默认读取镜像内 `/usr/share/nginx/html`。

因此：

- 仅挂载 `frontend/src` 或 `frontend` 到 `/web`，页面不会自动更新。
- 改了前端代码后，要么重建前端镜像，要么把 `dist` 挂载到 Nginx 根目录。

方式 A：重建前端镜像（推荐）

```bash
docker build -t clue-frontend:1.0.0 -f clue_ui_sandbox/frontend/Dockerfile .
cd clue_ui_sandbox/deploy
docker compose up -d --force-recreate frontend
```

方式 B：宿主机打包 + 挂载 `dist`（免重建镜像）

1. 在宿主机执行：

```bash
cd /data1/qwen2v/road_property_rightsmodel/clue_ui_sandbox/frontend
npm install
npm run build
```

2. `docker-compose.yml` 前端改为：

```yaml
frontend:
  image: clue-frontend:1.0.0
  volumes:
    - /data1/qwen2v/road_property_rightsmodel/clue_ui_sandbox/frontend/dist:/usr/share/nginx/html
  ports:
    - "6586:80"
```

3. 重新创建前端容器：

```bash
cd /data1/qwen2v/road_property_rightsmodel/clue_ui_sandbox/deploy
docker compose up -d --force-recreate frontend
```

## 7. 常用容器重启与更新命令

在 `clue_ui_sandbox/deploy` 目录执行。

### 7.1 重启全部容器

```bash
docker compose restart
```

### 7.2 只重启后端

```bash
docker compose restart backend
```

### 7.3 只重启前端

```bash
docker compose restart frontend
```

### 7.4 端口/挂载变更后，强制重建后端容器

```bash
docker compose up -d --force-recreate backend
```

### 7.5 同时重建前后端容器

```bash
docker compose up -d --force-recreate
```

### 7.6 查看容器状态

```bash
docker compose ps
```

### 7.7 查看后端日志

```bash
docker compose logs -f backend
```

### 7.8 查看前端日志

```bash
docker compose logs -f frontend
```

## 8. 故障排查速查

1. `healthz` 打不开：先执行 `docker compose ps` 确认 `6587->8000` 映射是否存在。
2. 改了 `docker-compose.yml` 端口/挂载后无效：用 `up -d --force-recreate`，仅 `restart` 不会应用新映射。
3. 前端页面没变化：确认是否是 Nginx 静态模式；静态模式下需要重建前端镜像或挂载 `dist`。
4. 前端页面正常但接口报错：查看 `docker compose logs -f backend`。
5. 本机通、外网不通：检查服务器防火墙/安全组是否放行 `6586` 和 `6587`。
