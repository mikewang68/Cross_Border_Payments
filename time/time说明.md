## time 模块项目说明

### 概览
`time/` 模块负责：
- 从 GSalary 平台拉取卡片/钱包相关业务数据
- 将数据扁平化后写入本地 MySQL
- 按配置的周期循环执行上述任务
- 将卡交易明细通过 Telegram 机器人实时推送给指定用户

主要文件：
- `async.py`：异步主循环与各项抓取/更新任务入口
- `gsalay_api.py`：封装 GSalary API 请求与签名
- `db_api.py`：MySQL 访问（查询/插入/更新/删除）
- `flat_data.py`：数据格式化与消息文本格式化
- `tele_push.py`：Telegram 推送逻辑
- `utils.py`：工具函数（环境变量读取、字典扁平化等）

日志：
- 运行/错误日志：`async.log`、`error.log`（同目录生成）

### 运行机制
`async.py` 启动后循环执行：
1. 读取平台列表（`async_ctrl.version`）
2. 读取执行周期（`async_ctrl.async_time`），默认每轮间隔 `time` 秒
3. 对每个 `version` 并发执行任务：
   - 交易明细：`card_transactions()`（卡片）；`wallet_transactions()`（钱包）
   - 余额：`wallet_balance()`；`balance_history()`
   - 卡基础信息：`cards_insert()`、`cards_update()`
   - 卡详细信息：`cards_info_insert()`、`cards_info_update()`
   - 卡安全信息：`cards_secure_info_insert()`、`cards_secure_info_update()`
   - Telegram 实时推送：`push_tele_messages()`（内部调用 `tele_push.push_card_transactions`）

循环体结尾 `await asyncio.sleep(time)` 等待下轮。

### 外部依赖与前置条件
1. 环境变量（读取自 `.env`）：
   - 数据库：`DB_USER`、`DB_PASSWORD`、`DB_HOST`、`DB_PORT`、`DB_DATABASE`
   - Telegram：`BOT_TOKEN`
   > 缺失将记录错误并停止相应功能。

2. 数据库表（关键字段，实际以库中表结构为准）：
   - `async_ctrl(version, async_time, ...)`：控制平台与周期
   - `cards(card_id, status, version, ...)`
   - `card_holder(card_holder_id, version, ...)`
   - `cards_info(card_id, ..., version)`
   - `cards_secure_info(card_id, ..., version)`
   - `wallet_balance(currency, amount, available, version, ...)`
   - `wallet_transactions(...)`
   - `balance_history(...)`
   - `card_transactions(insert_time, ..., version)`
   - `push_ctrl(function, last_insert_time)`：推送游标表
   - `system_key(system, appid, key)`：GSalary 鉴权所需秘钥与应用ID

3. Python 运行环境：
   - Python 3.11（当前虚拟环境）
   - 安装 `time/requirements.txt` 中依赖

### 核心组件说明
1. gsalary_api
   - `GSalaryAPI.make_gsalary_request(...)` 完成时间戳、Body Hash、RSA2 签名与请求发送
   - 主要接口：钱包余额、交易、汇率、卡片（申请/查询/更新/冻结）等
   - 依赖 `system_key` 表提供 `appid` 与 `key`（私钥，PEM 文本中的 `\n` 需正常存储）

2. db_api
   - 统一 MySQL 连接与 CRUD 封装
   - `insert_database` 会过滤不存在的列并用反引号处理 `key` 字段
   - `batch_update_database` 支持以单/双条件批量更新
   - 多种查询封装：单字段、全量、范围、匹配（含 `>`, `<`）

3. flat_data
   - `flat_data(version, json_data, p1, p2)`：将嵌套 JSON 扁平化，并追加 `insert_time`（精确到微秒）与 `version`
   - `flat_messages(data, region)`：按 `CN/JP/US` 渲染交易提示文本

4. tele_push
   - 读取 `BOT_TOKEN`，调用 `https://api.telegram.org/bot.../sendMessage`
   - 依据 `push_ctrl.last_insert_time` 推送增量交易，成功后更新游标

5. async（主调度）
   - 通过 `query_version()` 获取所有平台版本列表
   - 通过 `async_time()` 读取每轮周期 `time`
   - `asyncio.gather` 并发执行各子任务；每轮结束 sleep

### 运行步骤
1. 准备 `.env`（示例）：
   ```env
   DB_USER=root
   DB_PASSWORD=your_password
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_DATABASE=your_db

   BOT_TOKEN=123456:ABC-DEF...
   ```
2. 确保数据库表结构与 `system_key`、`async_ctrl`、`push_ctrl` 等数据准备就绪
3. 安装依赖：
   ```bash
   /root/test/time/07cc694b9b3fc636710fa08b6922c42b_venv/bin/pip install -r /root/test/date/requirements.txt
   ```
4. 运行：
   ```bash
   python /root/test/time/async.py
   ```

### 日志与排错
- 查看 `async.log`、`error.log` 获取异常详细
- 常见问题：
  - 环境变量缺失 → utils.get_db/get_tele_token 报错
  - `system_key` 中 `appid/key` 缺失或格式不对 → 请求签名失败
  - 表结构与字段不一致 → 插入/更新时记录过滤或报错
  - `push_ctrl.last_insert_time` 未初始化 → 首次推送逻辑需注意游标起点

### 安全注意
- 私钥仅存储在 `system_key.key`，并限制 DB 权限
- `.env` 文件不要提交到版本库

### 目录与文件
- `logs/`：日志目录（如果存在）
- 其余源码位于当前目录

