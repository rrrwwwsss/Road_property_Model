# clue_ui_sandbox 开发说明

## 架构

- `backend/`：FastAPI
- `frontend/`：Vue3 + Vite + Element Plus
- 本系统独立运行，不依赖仓库其他模块导入。

## 固定数据源

- SQLite：`pic/database/wupin_tanwei_dabt.db`
- 表：`results`
- 主键：`id`
- 图片字段：`图片路径`（HTTP URL，前端直显）

## 关键接口

- `GET /api/clues`
- `GET /api/clues/{id}`
- `POST /api/clues/{id}/commit`
- `GET /api/stats/summary`
- `GET /api/stats/by-violation`
- `GET /api/stats/by-location`
- `GET /api/stats/trend-by-violation`

## 提交模式

- `CLUE_COMMIT_GATEWAY=mock`：仅更新本地 `is_committed=1`
- `CLUE_COMMIT_GATEWAY=dm`：通过 `dmPython` 写入太极库
  - `OFFSITE_WARNS_HB`
  - `OFFSITE_INTELLECT_ERRORS_HB`

## 启动

```powershell
cd clue_ui_sandbox/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```powershell
cd clue_ui_sandbox/frontend
npm install
npm run dev
```

