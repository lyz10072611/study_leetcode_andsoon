"""
数字人项目端到端性能压测客户端（方案A）

功能：
- 使用 WebRTC 建立与数字人服务的连接（/offer 获取 sessionid）
- 通过 WebSocket 监听 LLM 文本首包（llm_text）
- 通过 WebRTC 远端音频轨监听 TTS 音频首包
- 并发运行 N 个会话，每会话发送 M 个交互请求
- 记录文本首包延迟（t_text_first）和音频首包延迟（t_audio_first）
- 输出 CSV 结果，包含 sessionid/utterance_id/timestamps/延迟/成功状态
- 计算并打印统计摘要：P50/P90/P95/P99 延迟、吞吐量

适配说明：
- 本脚本针对 digitalhuman4 项目的架构设计
- WebRTC 承载音视频，WebSocket 仅推送文本/图片
- 需要先调用 /offer 建立会话，然后才能使用其他接口
"""

import argparse
import asyncio
import websockets
import json
import uuid
import time
import csv
import os
import aiohttp
from statistics import median, quantiles
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration
from aiortc.mediastreams import MediaStreamTrack
from av import AudioFrame

# ---- Helpers ----
def now_ms():
    """获取当前时间戳（毫秒）"""
    return int(time.time() * 1000)


class AudioReceiver(MediaStreamTrack):
    """
    WebRTC 音频接收器
    用于监听远端音频轨的第一帧到达时间
    """
    kind = "audio"

    def __init__(self, on_first_frame_callback):
        super().__init__()
        self.on_first_frame = on_first_frame_callback
        self.first_frame_received = False

    async def recv(self):
        """接收音频帧"""
        frame = await super().recv()
        if not self.first_frame_received and self.on_first_frame:
            self.first_frame_received = True
            self.on_first_frame(now_ms())
        return frame


# ---- Session / Worker ----
class DigitalHumanSession:
    """
    数字人测试会话类
    每个会话独立运行，包含：
    - WebRTC 连接（音视频）
    - WebSocket 连接（文本/图片推送）
    - HTTP 客户端（触发交互）
    """
    def __init__(self, session_idx, cfg, csv_writer, csv_lock):
        self.session_idx = session_idx  # 会话索引（0-based）
        self.cfg = cfg
        self.csv_writer = csv_writer
        self.csv_lock = csv_lock

        # WebRTC 相关
        self.pc = None
        self.server_sessionid = None  # 服务端分配的 6 位 sessionid

        # WebSocket 相关
        self.ws = None
        self.running = True

        # 当前请求追踪（utterance_id -> state dict）
        self.utts = {}
        self.current_utterance_id = None  # 当前正在处理的 utterance_id

    async def run(self):
        """
        会话主循环：
        1. 建立 WebRTC 连接（/offer）
        2. 建立 WebSocket 连接（/ws）
        3. 循环发送交互请求（/human）
        4. 监听文本首包和音频首包
        5. 记录结果到 CSV
        """
        try:
            # 步骤 1: 建立 WebRTC 连接
            await self._setup_webrtc()
            if not self.server_sessionid:
                print(f"[会话{self.session_idx}] WebRTC 建立失败")
                return

            print(f"[会话{self.session_idx}] WebRTC 已建立, sessionid={self.server_sessionid}")

            # 步骤 2: 建立 WebSocket 连接并启动接收器
            ws_url = f"{self.cfg['ws_url']}?sessionid={self.server_sessionid}"
            async with websockets.connect(ws_url) as ws:
                self.ws = ws
                print(f"[会话{self.session_idx}] WebSocket 已连接")

                # 启动 WebSocket 接收器
                ws_receiver = asyncio.create_task(self._ws_receiver())

                # 步骤 3: 循环发送交互请求
                try:
                    await self._send_requests()
                finally:
                    self.running = False
                    ws_receiver.cancel()
                    try:
                        await ws_receiver
                    except asyncio.CancelledError:
                        pass

        except Exception as e:
            print(f"[会话{self.session_idx}] 异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 清理 WebRTC 连接
            if self.pc:
                await self.pc.close()

    async def _setup_webrtc(self):
        """
        建立 WebRTC 连接
        1. 创建 RTCPeerConnection
        2. 创建 offer
        3. 调用 /offer 接口获取 answer 和 sessionid
        4. 设置远端描述
        5. 监听远端音频轨
        """
        try:
            # 创建 PeerConnection
            self.pc = RTCPeerConnection()

            # 添加音频接收器监听远端音频轨
            @self.pc.on("track")
            async def on_track(track):
                if track.kind == "audio":
                    print(f"[会话{self.session_idx}] 接收到远端音频轨")
                    # 开始接收音频帧
                    while True:
                        try:
                            frame = await track.recv()
                            # 如果有当前正在处理的 utterance，记录音频首帧
                            if self.current_utterance_id and self.current_utterance_id in self.utts:
                                state = self.utts[self.current_utterance_id]
                                if state.get("t_audio_first_ms") is None:
                                    state["t_audio_first_ms"] = now_ms()
                                    print(f"[会话{self.session_idx}] 收到音频首帧: {self.current_utterance_id}")
                        except Exception as e:
                            break

            # 添加一个虚拟音频轨（有些服务端可能需要）
            # self.pc.addTransceiver("audio", direction="recvonly")

            # 创建 offer
            offer = await self.pc.createOffer()
            await self.pc.setLocalDescription(offer)

            # 调用 /offer 接口
            base_url = self.cfg["base_url"]
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/offer",
                    json={
                        "sdp": self.pc.localDescription.sdp,
                        "type": self.pc.localDescription.type
                    }
                ) as resp:
                    if resp.status != 200:
                        print(f"[会话{self.session_idx}] /offer 失败: {resp.status}")
                        return

                    data = await resp.json()
                    self.server_sessionid = data["sessionid"]

                    # 设置远端描述
                    answer = RTCSessionDescription(
                        sdp=data["sdp"],
                        type=data["type"]
                    )
                    await self.pc.setRemoteDescription(answer)

        except Exception as e:
            print(f"[会话{self.session_idx}] WebRTC 建立失败: {e}")
            import traceback
            traceback.print_exc()

    async def _ws_receiver(self):
        """
        WebSocket 接收器：监听服务端推送的文本和图片
        主要关注 llm_text 首包，用于计算文本首包延迟
        """
        try:
            async for raw in self.ws:
                ts = now_ms()

                try:
                    msg = json.loads(raw)
                    msg_type = msg.get("type")

                    if msg_type == "connected":
                        print(f"[会话{self.session_idx}] WebSocket 已确认连接")

                    elif msg_type == "llm_text":
                        # LLM 文本首包
                        text = msg.get("text", "")
                        if self.current_utterance_id and self.current_utterance_id in self.utts:
                            state = self.utts[self.current_utterance_id]
                            if state.get("t_text_first_ms") is None and text:
                                state["t_text_first_ms"] = ts
                                print(f"[会话{self.session_idx}] 收到文本首包: {self.current_utterance_id}, text={text[:30]}...")

                    elif msg_type == "llm_image":
                        # 图片消息（可选记录）
                        pass

                except json.JSONDecodeError:
                    pass

        except asyncio.CancelledError:
            return
        except Exception as e:
            print(f"[会话{self.session_idx}] WebSocket 接收器异常: {e}")

    async def _send_requests(self):
        """
        循环发送交互请求
        支持两种模式：
        1. chat 模式：发送文本，触发 LLM + TTS
        2. echo 模式：发送文本，直接 TTS（跳过 LLM）
        """
        max_requests = self.cfg.get("requests_per_session", 10)
        prompts = self.cfg.get("prompts", ["你好", "今天天气怎么样", "讲个笑话"])
        mode = self.cfg.get("trigger_mode", "chat")  # chat 或 echo
        request_interval = self.cfg.get("request_interval_ms", 1000) / 1000.0  # 转为秒
        timeout_ms = self.cfg.get("request_timeout_ms", 15000)

        base_url = self.cfg["base_url"]

        for i in range(max_requests):
            # 生成 utterance_id
            utt_id = str(uuid.uuid4())
            prompt = prompts[i % len(prompts)]

            # 初始化状态
            self.utts[utt_id] = {
                "session_idx": self.session_idx,
                "server_sessionid": self.server_sessionid,
                "utterance_id": utt_id,
                "prompt": prompt,
                "t_start_ms": None,
                "t_text_first_ms": None,
                "t_audio_first_ms": None,
                "completed": False,
                "notes": ""
            }

            self.current_utterance_id = utt_id
            t0 = now_ms()
            self.utts[utt_id]["t_start_ms"] = t0

            # 调用 /human 接口
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{base_url}/human",
                        json={
                            "sessionid": self.server_sessionid,
                            "type": mode,
                            "text": prompt,
                            "interrupt": False
                        },
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as resp:
                        if resp.status != 200:
                            self.utts[utt_id]["notes"] = f"HTTP {resp.status}"
                            print(f"[会话{self.session_idx}] /human 失败: {resp.status}")
                        else:
                            print(f"[会话{self.session_idx}] 已发送请求 {i+1}/{max_requests}: {prompt[:20]}...")
            except Exception as e:
                self.utts[utt_id]["notes"] = f"request error: {e}"
                print(f"[会话{self.session_idx}] 请求异常: {e}")

            # 等待响应（文本首包或音频首包）
            start_wait = now_ms()
            while True:
                state = self.utts[utt_id]

                # 如果收到了文本首包或音频首包，视为完成
                if state.get("t_text_first_ms") or state.get("t_audio_first_ms"):
                    state["completed"] = True
                    await self._write_csv_row(state)
                    break

                if now_ms() - start_wait > timeout_ms:
                    state["completed"] = False
                    state["notes"] = state.get("notes", "") + " timeout"
                    await self._write_csv_row(state)
                    break

                await asyncio.sleep(0.01)

            # 请求间隔
            if i < max_requests - 1:
                await asyncio.sleep(request_interval)

    async def _write_csv_row(self, state):
        """
        将单次请求的结果写入 CSV
        记录文本首包延迟和音频首包延迟
        """
        t_start = state["t_start_ms"]
        t_text = state.get("t_text_first_ms")
        t_audio = state.get("t_audio_first_ms")

        row = {
            "session_idx": state["session_idx"],
            "server_sessionid": state["server_sessionid"],
            "utterance_id": state["utterance_id"],
            "prompt": state["prompt"],
            "t_start_ms": t_start,
            "t_text_first_ms": t_text,
            "t_audio_first_ms": t_audio,
            "text_delay_ms": (t_text - t_start) if t_text and t_start else None,
            "audio_delay_ms": (t_audio - t_start) if t_audio and t_start else None,
            "completed": state["completed"],
            "notes": state["notes"],
        }

        async with self.csv_lock:
            self.csv_writer.writerow(row)


# ---- Orchestrator for running many sessions ----
async def run_benchmark(cfg):
    """
    测试总控函数
    创建并管理多个并发会话
    """
    concurrency = cfg.get("concurrency", 5)

    # 准备输出 CSV 文件
    out_csv = cfg.get("output_csv", "results.csv")
    csv_file = open(out_csv, "w", newline='', encoding='utf-8')
    fieldnames = [
        "session_idx", "server_sessionid", "utterance_id", "prompt",
        "t_start_ms", "t_text_first_ms", "t_audio_first_ms",
        "text_delay_ms", "audio_delay_ms", "completed", "notes"
    ]
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    csv_lock = asyncio.Lock()

    print(f"\n{'='*60}")
    print(f"开始压测: {concurrency} 路并发")
    print(f"{'='*60}\n")

    # 创建多个会话实例
    sessions = []
    for i in range(concurrency):
        sess = DigitalHumanSession(
            session_idx=i,
            cfg=cfg,
            csv_writer=csv_writer,
            csv_lock=csv_lock
        )
        sessions.append(sess)

    # 并发运行所有会话
    start_time = time.time()
    tasks = [asyncio.create_task(s.run()) for s in sessions]
    await asyncio.gather(*tasks, return_exceptions=True)
    elapsed = time.time() - start_time

    csv_file.close()

    print(f"\n{'='*60}")
    print(f"所有会话完成，耗时: {elapsed:.1f}秒")
    print(f"结果已保存至: {out_csv}")
    print(f"{'='*60}\n")

    # 生成统计摘要
    summarize_results(out_csv)


def summarize_results(csv_path):
    """
    分析测试结果，生成统计摘要
    统计文本首包延迟和音频首包延迟
    """
    try:
        import pandas as pd
    except ImportError:
        print("pandas 未安装，跳过统计摘要")
        return

    df = pd.read_csv(csv_path)

    total = len(df)
    completed = df['completed'].sum()

    def pct(n, total):
        return 0 if total == 0 else n / total

    print("\n" + "="*60)
    print("测试结果摘要")
    print("="*60)
    print(f"总请求数: {total}")
    print(f"成功完成: {completed} ({pct(completed, total)*100:.2f}%)")

    # 文本首包延迟统计
    text_delays = df[df['text_delay_ms'].notnull()]['text_delay_ms'].astype(float).values
    if len(text_delays) > 0:
        print(f"\n📝 文本首包延迟统计 (ms):")
        print(f"  样本数:  {len(text_delays)}")
        print(f"  平均值:  {text_delays.mean():.1f}")
        print(f"  P50:     {pd.Series(text_delays).quantile(0.5):.1f}")
        print(f"  P90:     {pd.Series(text_delays).quantile(0.9):.1f}")
        print(f"  P95:     {pd.Series(text_delays).quantile(0.95):.1f}  ⭐ SLA 指标")
        print(f"  P99:     {pd.Series(text_delays).quantile(0.99):.1f}")
        print(f"  最小值:  {text_delays.min():.1f}")
        print(f"  最大值:  {text_delays.max():.1f}")
    else:
        print("\n📝 文本首包延迟: 无有效数据")

    # 音频首包延迟统计
    audio_delays = df[df['audio_delay_ms'].notnull()]['audio_delay_ms'].astype(float).values
    if len(audio_delays) > 0:
        print(f"\n🔊 音频首包延迟统计 (ms):")
        print(f"  样本数:  {len(audio_delays)}")
        print(f"  平均值:  {audio_delays.mean():.1f}")
        print(f"  P50:     {pd.Series(audio_delays).quantile(0.5):.1f}")
        print(f"  P90:     {pd.Series(audio_delays).quantile(0.9):.1f}")
        print(f"  P95:     {pd.Series(audio_delays).quantile(0.95):.1f}  ⭐ SLA 指标")
        print(f"  P99:     {pd.Series(audio_delays).quantile(0.99):.1f}")
        print(f"  最小值:  {audio_delays.min():.1f}")
        print(f"  最大值:  {audio_delays.max():.1f}")
    else:
        print("\n🔊 音频首包延迟: 无有效数据")

    # 吞吐量统计
    if completed > 0:
        tmin = df['t_start_ms'].min()
        tmax_text = df['t_text_first_ms'].max() if df['t_text_first_ms'].notnull().any() else None
        tmax_audio = df['t_audio_first_ms'].max() if df['t_audio_first_ms'].notnull().any() else None
        tmax = max([t for t in [tmax_text, tmax_audio] if pd.notnull(t)], default=df['t_start_ms'].max())

        if pd.notnull(tmin) and pd.notnull(tmax) and tmax > tmin:
            duration_s = (tmax - tmin) / 1000.0
            throughput = completed / duration_s
            print(f"\n📊 吞吐量统计:")
            print(f"  测试时长:  {duration_s:.1f}秒")
            print(f"  吞吐量:    {throughput:.2f} 请求/秒")
            print(f"  并发会话:  {df['session_idx'].nunique()}")

    print("="*60)


# ---- CLI / Config parsing ----
def load_config(path):
    """加载 JSON 配置文件"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    """
    命令行入口点
    支持从配置文件或命令行参数运行压测
    """
    parser = argparse.ArgumentParser(
        description="数字人项目端到端性能压测客户端",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 使用配置文件
  python test.py --config config.json
  
  # 使用命令行参数（快速测试）
  python test.py --base-url http://localhost:8010 --concurrency 5 --requests 10
  
  # 混合使用
  python test.py --config config.json --concurrency 10
        """
    )

    # 配置文件选项
    parser.add_argument("--config", "-c", help="JSON 配置文件路径")

    # 基本选项
    parser.add_argument("--base-url", help="服务器地址，如 http://localhost:8010")
    parser.add_argument("--concurrency", type=int, help="并发会话数，默认 5")
    parser.add_argument("--requests", type=int, help="每会话请求数，默认 10")
    parser.add_argument("--mode", choices=["chat", "echo"], help="交互模式：chat（LLM+TTS）或 echo（仅TTS）")
    parser.add_argument("--prompts", nargs="+", help="测试提示词列表")
    parser.add_argument("--output", "-o", help="输出 CSV 文件路径，默认 results.csv")
    parser.add_argument("--timeout", type=int, help="单个请求超时（毫秒），默认 15000")
    parser.add_argument("--interval", type=int, help="请求间隔（毫秒），默认 1000")

    args = parser.parse_args()

    # 加载配置
    if args.config:
        cfg = load_config(args.config)
    else:
        cfg = {}

    # 命令行参数覆盖配置文件
    if args.base_url:
        cfg["base_url"] = args.base_url
    if args.concurrency:
        cfg["concurrency"] = args.concurrency
    if args.requests:
        cfg["requests_per_session"] = args.requests
    if args.mode:
        cfg["trigger_mode"] = args.mode
    if args.prompts:
        cfg["prompts"] = args.prompts
    if args.output:
        cfg["output_csv"] = args.output
    if args.timeout:
        cfg["request_timeout_ms"] = args.timeout
    if args.interval:
        cfg["request_interval_ms"] = args.interval

    # 设置默认值
    cfg.setdefault("base_url", "http://localhost:8010")
    cfg.setdefault("concurrency", 5)
    cfg.setdefault("requests_per_session", 10)
    cfg.setdefault("trigger_mode", "chat")
    cfg.setdefault("prompts", [
        "你好，很高兴见到你",
        "今天天气怎么样",
        "能给我讲个笑话吗",
        "你最喜欢什么颜色",
        "推荐一本好书"
    ])
    cfg.setdefault("output_csv", "results.csv")
    cfg.setdefault("request_timeout_ms", 15000)
    cfg.setdefault("request_interval_ms", 1000)

    # 构造 WebSocket URL
    base_url = cfg["base_url"]
    ws_scheme = "wss" if base_url.startswith("https") else "ws"
    ws_host = base_url.replace("http://", "").replace("https://", "")
    cfg["ws_url"] = f"{ws_scheme}://{ws_host}/ws"

    # 验证必需参数
    if not cfg.get("base_url"):
        parser.error("错误: 必须指定 --base-url 或在配置文件中指定 base_url")

    print(f"\n配置:")
    print(f"  服务器地址: {cfg['base_url']}")
    print(f"  并发会话数: {cfg['concurrency']}")
    print(f"  每会话请求: {cfg['requests_per_session']}")
    print(f"  交互模式:   {cfg['trigger_mode']}")
    print(f"  输出文件:   {cfg['output_csv']}")

    # 运行压测
    asyncio.run(run_benchmark(cfg))


if __name__ == "__main__":
    main()