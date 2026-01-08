import lark_oapi as lark
from lark_oapi.api.aily.v1 import *
import uuid
import time
from typing import Optional, Generator
from logger import logger
import threading
import queue
from lark_oapi.api.aily.v1.model.list_aily_session_aily_message_request import ListAilySessionAilyMessageRequest


class AilyChatBotStream:
    """
    飞书Aily智能对话机器人封装类（支持流式生成 yield）。
    用法：
        bot = AilyChatBotStream(app_id, app_secret, bot_id)
        bot.create_session()
        for chunk in bot.chat_stream("你好"):
            print(chunk, end="", flush=True)
    """
    def __init__(self, app_id: str, app_secret: str, bot_id: str, log_level: int = lark.LogLevel.INFO,
                 poll_max: int = 300, poll_interval: float = 0.05):
        self.app_id = app_id
        self.app_secret = app_secret
        self.bot_id = bot_id
        self.log_level = log_level
        self.client = lark.Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .log_level(self.log_level) \
            .build()
        self.session_id: Optional[str] = None
        self.poll_max = poll_max
        self.poll_interval = poll_interval
        self.aily_session_request = GetAilySessionAilyMessageRequest.builder().aily_session_id(self.session_id)

    def create_session(self) -> str:
        req_body = CreateAilySessionRequestBody.builder().channel_context("{}").metadata("{}").build()
        req = CreateAilySessionRequest.builder().request_body(req_body).build()
        resp = self.client.aily.v1.aily_session.create(req)
        if not resp.success():
            raise RuntimeError(f"创建会话失败: {resp.code}, {resp.msg}")
        self.session_id = resp.data.session.id
        return self.session_id

    def send_message(self, text: str) -> str:
        if not self.session_id:
            raise RuntimeError("请先调用 create_session() 创建会话")
        start_time = time.time()
        req_body = CreateAilySessionAilyMessageRequestBody.builder() \
            .idempotent_id(str(uuid.uuid4())) \
            .content_type("MDX") \
            .content(text) \
            .build()
        req = CreateAilySessionAilyMessageRequest.builder() \
            .aily_session_id(self.session_id) \
            .request_body(req_body).build()
        resp = self.client.aily.v1.aily_session_aily_message.create(req)
        send_time = (time.time() - start_time) * 1000
        logger.info(f"send_message 耗时: {send_time:.2f}ms")
        if not resp.success():
            raise RuntimeError(f"发送消息失败: {resp.code}, {resp.msg}")
        return resp.data.message.id

    def trigger_bot_response(self, result_queue: queue.Queue):
        if not self.session_id:
            raise RuntimeError("请先调用 create_session() 创建会话")
        start_time = time.time()
        req_body = CreateAilySessionRunRequestBody.builder().app_id(self.bot_id).build()
        req = CreateAilySessionRunRequest.builder().aily_session_id(self.session_id).request_body(req_body).build()
        resp = self.client.aily.v1.aily_session_run.create(req)
        trigger_time = (time.time() - start_time) * 1000
        logger.info(f"trigger_bot_response 耗时: {trigger_time:.2f}ms")
        if not resp.success():
            raise RuntimeError(f"触发机器人回复失败: {resp.code}, {resp.msg}")
        result_queue.put(resp.data.run.id)

    def _poll_stream(self, run_id: str) -> Generator[str, None, str]:
        """
        内部方法：流式轮询 Bot 输出
        yield 每次增量内容，最终返回完整文本
        """
        

        last_content = ""
        total_content = ""
        status = ""
        latest_bot_message_id = None
        start_time = time.time()
        for _ in range(self.poll_max):
            time.sleep(self.poll_interval)
            
            # 查询 run 状态
            if len(str(total_content)) > 1 or status != "IN_PROGRESS":
                get_run_req = GetAilySessionRunRequest.builder().aily_session_id(self.session_id).run_id(run_id).build()
                run_resp = self.client.aily.v1.aily_session_run.get(get_run_req)
                if not (run_resp.success() and run_resp.data and run_resp.data.run):
                    continue
                status = run_resp.data.run.status
                logger.info(f"Polling  status: {status}")

            if status in ["IN_PROGRESS", "COMPLETED"]:
                # 拉取增量消息
                msg_list_req = ListAilySessionAilyMessageRequest.builder() \
                    .aily_session_id(self.session_id) \
                    .run_id(run_id) \
                    .with_partial_message(True) \
                    .build()
                msg_list_resp = self.client.aily.v1.aily_session_aily_message.list(msg_list_req)

                if msg_list_resp.success() and msg_list_resp.data and msg_list_resp.data.messages:
                    for msg in msg_list_resp.data.messages:
                        if getattr(getattr(msg, 'sender', None), 'sender_type', '') == 'ASSISTANT':
                            content = getattr(msg, 'content', '') or ''
                            logger.info(f"Polling  content: {content}")
                            if content != last_content:
                                yield content[len(last_content):]  # 增量 yield
                                last_content = content
                                total_content += content
                            latest_bot_message_id = getattr(msg, 'id', None)

            if status in ["COMPLETED", "FAILED", "CANCELLED", "EXPIRED"]:
                break

        # 最终精确获取完整 Bot 内容
        return total_content

    def fetch_last_message(self, message_id: str) -> str:
        """
        获取指定 Bot 消息的最终完整文本（plain_text 优先）
        """
        if not message_id:
            return ""
        max_retry = 1
        delay = 0.2
        for _ in range(max_retry):
            time.sleep(delay)
            req = self.aily_session_request.aily_message_id(message_id).build()
            resp = self.client.aily.v1.aily_session_aily_message.get(req)
            if resp.success() and resp.data and resp.data.message:
                plain_text = getattr(resp.data.message, 'plain_text', '') or ''
                if plain_text:
                    return plain_text
                content = getattr(resp.data.message, 'content', '') or ''
                if content:
                    return content
        return "(未获取到Aily回复)"

    def chat_stream(self, text: str) -> Generator[str, None, str]:
        """
        流式对话生成器，边生成边返回内容
        使用方法:
            for chunk in bot.chat_stream("你好"):
                print(chunk, end="", flush=True)
        """
        if not self.session_id:
            self.create_session()
        _ = self.send_message(text)
        result_queue = queue.Queue()
        # 启动线程触发机器人回复
        t = threading.Thread(target=self.trigger_bot_response, args=(result_queue,))
        t.start()
        run_id = result_queue.get()
        final_text = yield from self._poll_stream(run_id)
        return final_text


    def chat(self, text: str) -> str:
        """
        普通同步对话（非流式），返回完整文本
        """
        return "".join(chunk for chunk in self.chat_stream(text))

    def close_session(self) -> bool:
        self.session_id = None
        return True


# --- 使用示例 ---
def main():
    CONFIG = {
        "app_id": "cli_a98b607060e8d00d",
        "app_secret": "DGbTJaJU0zMX2AIXXb0jZfVsCghZmiJJ",
        "bot_id": "spring_9ed7666ebc__c",
    }
    bot = AilyChatBotStream(CONFIG["app_id"], CONFIG["app_secret"], CONFIG["bot_id"])
    bot.create_session()
    print(f"会话已创建: {bot.session_id}")

    while True:
        try:
            user_input = input("\nUser: ").strip()
            if user_input.lower() in ('退出', 'quit', 'exit'):
                break
            if not user_input:
                continue

            print("Aily: ", end="", flush=True)
            final_text = ""
            for chunk in bot.chat_stream(user_input):
                print(chunk, end="", flush=True)
                final_text += chunk
            print("\n[完整文本返回]:", final_text)

        except KeyboardInterrupt:
            print("\n对话结束")
            break
        except Exception as e:
            print("\n错误:", e)

    bot.close_session()


if __name__ == "__main__":
    main()
