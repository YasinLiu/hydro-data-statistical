# 水情数据统计 Web 程序（FastAPI）

基于 FastAPI 实现的“月到报统计”程序，支持：

- 按月查询每个站点每天的实到报段次（1~31 列）
- 右侧汇总列：`应到报`、`实到报`、`到报率(%)`
- 统计规则：先按 `Ctype` 映射应到报段次，再按站点 JSON 覆盖
- 只统计 `Sourcetype=1`
- Excel 导出
- 页面内编辑本地 JSON 配置

> 当前实现按 `stationid` 聚合（已按你的要求）

## 1. 环境准备（uv）

```bash
uv sync
```

## 2. 启动

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

浏览器访问：`http://127.0.0.1:8000`

## 3. 数据库配置（SQL Server）

默认连接参数已经按你提供值写入代码，可通过环境变量覆盖：

- `DB_HOST`（默认 `10.6.34.16`）
- `DB_PORT`（默认 `1433`）
- `DB_NAME`（默认 `CSRRDB`）
- `DB_USER`（默认 `sa`）
- `DB_PASSWORD`（默认 `xiangsiersheng`）
- `DB_DRIVER`（默认 `ODBC Driver 18 for SQL Server`）

示例：

```bash
DB_PASSWORD='your_password' uv run uvicorn app.main:app --reload
```

## 4. 本地规则配置

配置文件路径：`config/report_rules.json`

示例：

```json
{
  "default_daily_expected": 24,
  "ctype_daily_expected": {
    "RR": 24,
    "ZZ": 48
  },
  "station_overrides": {
    "A001": 48
  },
  "sourcetype_filter": "1"
}
```

说明：

1. 先读 `ctype_daily_expected[Ctype]`
2. 再用 `station_overrides[stationid]` 覆盖
3. 无匹配时使用 `default_daily_expected`

## 5. 测试

```bash
python3 -m pytest -q
```

## 6. 目录结构

- `app/main.py`：FastAPI 路由、导出逻辑、页面入口
- `app/db.py`：SQL Server 查询层
- `app/report_logic.py`：月统计核心逻辑（可单测）
- `app/config_store.py`：本地 JSON 配置加载/保存
- `templates/index.html`：页面
- `static/app.js`：前端查询/渲染/配置保存
- `static/app.css`：样式
- `config/report_rules.json`：规则文件
- `tests/`：核心逻辑测试

## 7. 说明

- 本版前端未引入 Vue（需求以报表渲染为主，原生 JS 足够且交付更快）。
- 若后续要加复杂交互（多维筛选、图表联动、权限、多页面），可以再升级到 Vue。
