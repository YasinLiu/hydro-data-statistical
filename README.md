# 水情数据统计 Web 程序（FastAPI）

## 项目背景

本项目用于生成“系统定时报据接收统计月报表”，核心目标是把分散在 SQL Server 中的原始到报数据，按业务口径汇总为可查询、可导出的月度报表。

业务上关注三个指标：

- `应到报`：站点当月理论应接收段次数
- `实到报`：站点当月实际接收段次数（按时段去重）
- `到报率(%)`：`实到报 / 应到报 * 100`

当前实现按 `stationid` 聚合，支持配置化规则（站型默认 + 站点覆盖），并支持按“水文日时间窗”统计（默认 `09:00` 到次日 `08:59`）。

---

## 功能概览

- 月报查询：按“年 + 月”查询每个站点的每日实到报段次（1~31 列）
- 汇总统计：输出 `应到报`、`实到报`、`到报率(%)`
- Excel 导出：一键导出当前月报
- 统计规则配置：页面可读取/修改本地 JSON 规则
- 数据过滤：仅统计 `Sourcetype=1`（可在配置中调整）

---

## 技术架构说明

### 1) 架构分层

- **展示层（Frontend）**：`templates/index.html` + `static/app.js` + `static/app.css`
  - 负责年月选择、结果展示、配置编辑、导出触发
- **接口层（FastAPI）**：`app/main.py`
  - 提供页面路由与 API
- **领域逻辑层（统计核心）**：`app/report_logic.py`
  - 负责时段映射、按日汇总、月度指标计算
- **数据访问层（Repository）**：`app/db.py`
  - 负责 SQL Server 查询站点与原始记录
- **配置层（本地 JSON）**：`app/config_store.py` + `config/report_rules.json`
  - 负责规则加载、规范化、持久化

### 2) 请求处理流程

1. 前端调用 `/api/report/monthly?year=YYYY&month=MM`
2. 后端读取 `report_rules.json`，解析 `day_start_hour` 与过滤条件
3. 后端按统计时间窗查询 `OneDayData`，并获取 `Stations`
4. `report_logic` 按站点逐日聚合（同站点同“应报时段”去重）
5. 返回 JSON 给前端渲染；或由 `/api/report/monthly/export` 生成 Excel

### 3) 关键统计口径

- **应到报段次来源**：
  - 先按 `ctype_daily_expected[Ctype]`
  - 再用 `station_overrides[stationid]` 覆盖
  - 无匹配时用 `default_daily_expected`
- **统计时间窗**：
  - `day_start_hour=9` 时，统计月范围为：
  - 当月 `1日09:00`（含）到次月 `1日09:00`（不含）
  - 当天统计归属通过“时间减去 day_start_hour 小时”后按自然日落桶
- **去重规则**：同站点、同统计日、同应报时段，仅计 1 次

---

## 项目结构

```text
app/
  main.py               # FastAPI 入口、API 路由、Excel 导出
  db.py                 # SQL Server 访问层
  report_logic.py       # 月报统计核心逻辑
  config_store.py       # JSON 配置加载/保存与规范化
  settings.py           # 数据库连接配置与连接串拼装
config/
  report_rules.json     # 统计规则配置
static/
  app.js                # 前端交互逻辑
  app.css               # 页面样式
templates/
  index.html            # 页面模板
tests/
  test_report_logic.py
  test_config_and_db_helpers.py
.data/
  Stations.sql
  OneDayData.sql
```

---

## 数据源与数据库说明

- 数据库：SQL Server
- 库名：`CSRRDB`
- 表：
  - `dbo.Stations`（站点基础信息）
  - `dbo.OneDayData`（原始到报数据）

程序当前使用字段：

- `Stations`: `StationID`, `Cname`, `Ctype`
- `OneDayData`: `stationid`, `datatime`, `Sourcetype`

> 注意：SQL 中对 `Sourcetype` 做了 `LTRIM/RTRIM` 后比对，兼容 char 字段尾空格。

---

## 部署说明

### 1) 环境要求

- 操作系统：Linux（推荐）/ Windows
- Python：`>=3.10`
- 包管理：`uv`
- 数据库驱动：`ODBC Driver 18 for SQL Server`
- 网络：应用机器可访问 SQL Server 地址与端口

### 2) 安装依赖

```bash
uv sync --extra dev
```

### 3) 配置数据库连接

通过环境变量覆盖默认连接（默认值写在 `app/settings.py`）：

- `DB_HOST`（默认 `10.6.34.16`）
- `DB_PORT`（默认 `1433`）
- `DB_NAME`（默认 `CSRRDB`）
- `DB_USER`（默认 `sa`）
- `DB_PASSWORD`（默认 `xiangsiersheng`）
- `DB_DRIVER`（默认 `ODBC Driver 18 for SQL Server`）

示例：

```bash
export DB_HOST=10.6.34.16
export DB_PORT=1433
export DB_NAME=CSRRDB
export DB_USER=sa
export DB_PASSWORD='***'
export DB_DRIVER='ODBC Driver 18 for SQL Server'
```

### 4) 启动方式

#### 开发模式

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 生产模式（示例）

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

访问地址：`http://<host>:8000`

### 5) systemd 部署示例（可选）

`/etc/systemd/system/hydro-report.service`：

```ini
[Unit]
Description=Hydro Monthly Report Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/hydro-data-statistical
Environment=DB_HOST=10.6.34.16
Environment=DB_PORT=1433
Environment=DB_NAME=CSRRDB
Environment=DB_USER=sa
Environment=DB_PASSWORD=***
ExecStart=/usr/bin/env uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启用命令：

```bash
sudo systemctl daemon-reload
sudo systemctl enable hydro-report
sudo systemctl start hydro-report
sudo systemctl status hydro-report
```

---

## 使用说明

### 1) 页面操作

1. 选择“年”“月”
2. 点击“查询”获取月报
3. 点击“导出 Excel”下载同口径报表
4. 点击“配置规则”可查看和修改本地配置

### 2) 配置文件说明

文件：`config/report_rules.json`

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
  "sourcetype_filter": "1",
  "day_start_hour": 9
}
```

字段解释：

- `default_daily_expected`: 默认每日应到报段次
- `ctype_daily_expected`: 按站型设置每日应到报段次
- `station_overrides`: 按站点覆盖每日应到报段次
- `sourcetype_filter`: 数据来源过滤值
- `day_start_hour`: 报表日开始小时（0~23）

### 3) API 说明

- `GET /api/report/monthly?year=2026&month=2`
  - 返回月报 JSON
- `GET /api/report/monthly/export?year=2026&month=2`
  - 下载 Excel
- `GET /api/config`
  - 获取当前配置
- `PUT /api/config`
  - 保存配置

配置更新示例：

```bash
curl -X PUT http://127.0.0.1:8000/api/config \
  -H 'Content-Type: application/json' \
  -d '{
    "default_daily_expected": 24,
    "ctype_daily_expected": {"RR": 24, "ZZ": 48},
    "station_overrides": {},
    "sourcetype_filter": "1",
    "day_start_hour": 9
  }'
```

---

## 测试与验证

运行测试：

```bash
python3 -m pytest -q
```

当前测试覆盖：

- 配置加载/保存与规范化
- 月统计时间窗边界
- 时段归属与去重逻辑

---

## 常见问题（FAQ）

### 1) 查询报错 `pyodbc is required`

未安装依赖，执行：

```bash
uv sync
```

### 2) 查询报错驱动不存在

请先安装 SQL Server ODBC 驱动，并确认 `DB_DRIVER` 与系统实际驱动名一致。

### 3) 某月数据全是 0

请检查：

- `sourcetype_filter` 是否与库中实际值一致
- `ctype_daily_expected` 的键是否与 `Stations.Ctype` 实际值一致
- `day_start_hour` 是否符合你的报表口径

---

## 版本与后续规划

当前版本：`v0.1.0`

后续可扩展方向：

- 增加缺报次数、漏报率等更多业务指标
- 增加按流域/站类筛选
- 增加登录鉴权与操作审计
- 如前端交互复杂度上升，再升级到 Vue
