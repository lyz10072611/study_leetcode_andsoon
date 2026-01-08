# 数字人项目端到端性能压测工具

## 功能说明

本工具用于测试数字人项目在并发场景下的性能指标，包括：
- **文本首包延迟**：从发送请求到收到 LLM 第一条文本的时间
- **音频首包延迟**：从发送请求到 WebRTC 音频轨收到第一帧的时间
- **系统吞吐量**：单位时间内系统能处理的请求数
- **稳定性指标**：P50/P90/P95/P99 延迟分布

## 依赖安装

```bash
pip install aiohttp websockets aiortc pandas
```

## 快速开始

### 方式 1：使用配置文件（推荐）

1. 编辑 `test_config.json`，设置服务器地址和测试参数
2. 运行测试：

```bash
python test.py --config test_config.json
```

### 方式 2：使用命令行参数

```bash
# 5路并发，每路10个请求
python test.py --base-url http://localhost:8010 --concurrency 5 --requests 10

# 自定义提示词
python test.py --base-url http://localhost:8010 --concurrency 5 --requests 10 \
  --prompts "你好" "今天天气怎么样" "讲个笑话"

# echo 模式（仅测试 TTS，跳过 LLM）
python test.py --base-url http://localhost:8010 --concurrency 5 --requests 10 --mode echo
```

## 配置参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `base_url` | 服务器地址 | `http://localhost:8010` |
| `concurrency` | 并发会话数 | `5` |
| `requests_per_session` | 每会话请求数 | `10` |
| `trigger_mode` | 交互模式：`chat`（LLM+TTS）或 `echo`（仅TTS） | `chat` |
| `prompts` | 测试提示词列表（循环使用） | 见配置文件 |
| `output_csv` | 输出 CSV 文件路径 | `results.csv` |
| `request_timeout_ms` | 单个请求超时（毫秒） | `15000` |
| `request_interval_ms` | 同一会话内请求间隔（毫秒） | `1000` |

## 测试流程

1. **建立 WebRTC 连接**：调用 `/offer` 接口，获取服务端分配的 `sessionid`
2. **建立 WebSocket 连接**：连接到 `/ws?sessionid=xxx`，监听文本推送
3. **发送交互请求**：调用 `/human` 接口触发 LLM + TTS 流程
4. **监听首包时间**：
   - 通过 WebSocket 接收 `llm_text` 消息（文本首包）
   - 通过 WebRTC 音频轨接收音频帧（音频首包）
5. **记录结果**：将延迟数据写入 CSV 文件
6. **生成统计报告**：计算 P50/P90/P95/P99 和吞吐量

## 输出结果

### CSV 文件字段

- `session_idx`: 会话索引（0-based）
- `server_sessionid`: 服务端分配的会话ID
- `utterance_id`: 请求唯一标识符（UUID）
- `prompt`: 发送的提示词
- `t_start_ms`: 请求发送时间（毫秒）
- `t_text_first_ms`: 文本首包到达时间
- `t_audio_first_ms`: 音频首包到达时间
- `text_delay_ms`: 文本首包延迟
- `audio_delay_ms`: 音频首包延迟
- `completed`: 是否成功完成
- `notes`: 备注信息（错误、超时等）

### 统计摘要

测试完成后会自动打印统计摘要，包括：

```
测试结果摘要
============================================================
总请求数: 50
成功完成: 48 (96.00%)

📝 文本首包延迟统计 (ms):
  样本数:  48
  平均值:  245.3
  P50:     230.5
  P90:     312.8
  P95:     356.2  ⭐ SLA 指标
  P99:     398.1
  最小值:  185.2
  最大值:  412.3

🔊 音频首包延迟统计 (ms):
  样本数:  48
  平均值:  892.1
  P50:     865.3
  P90:     1023.7
  P95:     1089.5  ⭐ SLA 指标
  P99:     1156.8
  最小值:  723.4
  最大值:  1198.2

📊 吞吐量统计:
  测试时长:  58.3秒
  吞吐量:    0.82 请求/秒
  并发会话:  5
============================================================
```

## 测试场景建议

### 1. 基准性能测试（5路并发）

```bash
python test.py --base-url http://localhost:8010 --concurrency 5 --requests 20
```

用于评估系统在典型负载下的表现。

### 2. 压力测试（10路并发）

```bash
python test.py --base-url http://localhost:8010 --concurrency 10 --requests 20
```

用于测试系统在高负载下的稳定性。

### 3. TTS 性能单独测试

```bash
python test.py --base-url http://localhost:8010 --concurrency 5 --requests 20 --mode echo
```

跳过 LLM，仅测试 TTS 性能。

### 4. 长时间稳定性测试

```bash
python test.py --base-url http://localhost:8010 --concurrency 3 --requests 100
```

用于评估系统在长时间运行下的稳定性。

## 注意事项

1. **确保服务端已启动**：压测前确认数字人服务正常运行
2. **避免过高并发**：初次测试建议从 5 路并发开始，逐步增加
3. **资源监控**：压测期间建议监控服务端 CPU、内存、GPU 使用率
4. **网络环境**：本地测试时延迟较低，远程测试需考虑网络延迟
5. **依赖版本**：建议使用 Python 3.8+ 和最新版本的依赖库

## 常见问题

### Q: 为什么音频首包延迟为空？
A: 可能的原因：
- WebRTC 连接未成功建立
- 服务端未返回音频流
- 音频轨接收超时

解决方法：检查服务端日志，确认 WebRTC 连接状态。

### Q: 为什么文本首包延迟为空？
A: 可能的原因：
- WebSocket 连接失败
- 使用了 `echo` 模式（不经过 LLM，无文本返回）
- LLM 响应超时

解决方法：检查 WebSocket 连接，确认 `trigger_mode` 为 `chat`。

### Q: 如何提高测试并发数？
A: 修改 `concurrency` 参数，但需注意：
- 并发数不宜超过服务端 `max_session` 配置
- 过高并发可能导致服务端资源耗尽
- 建议逐步增加并发数，观察系统表现

## 技术架构

```
┌─────────────┐
│  test.py    │  压测客户端
└──────┬──────┘
       │
       ├─── WebRTC ────────┐
       │                   ▼
       │            ┌──────────────┐
       │            │              │
       ├─── HTTP ───┤  数字人服务   │  (app.py)
       │            │              │
       └─── WS ─────┤  8010端口    │
                    └──────────────┘
                           │
                ┌──────────┼──────────┐
                │          │          │
             ┌──▼─┐    ┌──▼──┐   ┌──▼──┐
             │LLM │    │ TTS │   │视频 │
             └────┘    └─────┘   └─────┘
```

## 许可证

本工具仅供测试使用。

