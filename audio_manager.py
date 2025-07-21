import asyncio
import uuid
import time
import random
from typing import Optional, Dict, Any
import signal

import config
from realtime_dialog_client import RealtimeDialogClient



class DialogSession:
    """对话会话管理类"""

    def __init__(self, ws_config: Dict[str, Any]):
        self.session_id = str(uuid.uuid4())
        self.client = RealtimeDialogClient(config=ws_config, session_id=self.session_id)

        self.is_running = True
        self.is_session_finished = False
        self.is_user_querying = False
        self.is_sending_chat_tts_text = False
        self.audio_buffer = b''
        self.audio_callback = None


        signal.signal(signal.SIGINT, self._keyboard_signal)

    def feed_audio(self, data: bytes):
        # print("📥 feed_audio called")
        asyncio.create_task(self.client.task_request(data))

    def set_audio_callback(self, callback):
        self.audio_callback = callback

    async def start(self) -> None:
        try:
            await self.client.connect()
            asyncio.create_task(self.receive_loop())  # ✅ 只保留一个

            while self.is_running:
                await asyncio.sleep(0.1)

            await self.client.finish_session()
            while not self.is_session_finished:
                await asyncio.sleep(0.1)
            await self.client.finish_connection()
            await asyncio.sleep(0.1)
            await self.client.close()
            print(f"✅ 会话结束 logid: {self.client.logid}")
            save_audio_to_pcm_file(self.audio_buffer, "output.pcm")

        except Exception as e:
            print(f"💥 会话错误: {e}")


    async def receive_loop(self):
        try:
            while True:
                response = await self.client.receive_server_response()

                # === 普通消息 / 音频 / 状态
                self.handle_server_response(response)

                if 'event' in response and response['event'] in (152, 153):
                    print(f"🎯 会话结束事件: {response['event']}")
                    self.is_session_finished = True
                    break

        except asyncio.CancelledError:
            print("⚠️ 接收任务已取消")
        except Exception as e:
            print(f"💥 接收消息出错: {e}")





    def handle_server_response(self, response: Dict[str, Any]) -> None:
        if response == {}:
            return

        from backend import update_status
        event = response.get('event')
        if event is not None:
            update_status(event_id=event)

        if response['message_type'] == 'SERVER_ACK' and isinstance(response.get('payload_msg'), bytes):
            audio_data = response['payload_msg']
            
            # ✅ 发给前端
            if self.audio_callback:
                asyncio.create_task(self.audio_callback(audio_data))

            # ✅ 可选本地播放
            self.audio_buffer += audio_data
            return
        elif response['message_type'] == 'SERVER_FULL_RESPONSE':
            print(f"服务器响应: {response}")
            event = response.get('event')
            payload_msg = response.get('payload_msg', {})

            if event == 450:
                self.is_user_querying = True

            if event == 350 and self.is_sending_chat_tts_text and payload_msg.get("tts_type") == "chat_tts_text":
                self.is_sending_chat_tts_text = False

            if event == 459:
                self.is_user_querying = False
                if random.randint(0, 2) == 20:
                    self.is_sending_chat_tts_text = True
                    asyncio.create_task(self.trigger_chat_tts_text())

        elif response['message_type'] == 'SERVER_ERROR':
            print(f"服务器错误: {response['payload_msg']}")
            raise Exception("服务器错误")

    async def trigger_chat_tts_text(self):
        """概率触发发送ChatTTSText请求"""
        print("hit ChatTTSText event, start sending...")
        await self.client.chat_tts_text(
            is_user_querying=self.is_user_querying,
            start=True,
            end=False,
            content="这是第一轮TTS的开始和中间包事件，这两个合而为一了。",
        )
        await self.client.chat_tts_text(
            is_user_querying=self.is_user_querying,
            start=False,
            end=True,
            content="这是第一轮TTS的结束事件。",
        )
        await asyncio.sleep(10)
        await self.client.chat_tts_text(
            is_user_querying=self.is_user_querying,
            start=True,
            end=False,
            content="这是第二轮TTS的开始和中间包事件，这两个合而为一了。",
        )
        await self.client.chat_tts_text(
            is_user_querying=self.is_user_querying,
            start=False,
            end=True,
            content="这是第二轮TTS的结束事件。",
        )

    def _keyboard_signal(self, sig, frame):
        print(f"receive keyboard Ctrl+C")
        self.is_running = False


def save_audio_to_pcm_file(audio_data: bytes, filename: str) -> None:
    """保存原始PCM音频数据到文件"""
    if not audio_data:
        print("No audio data to save.")
        return
    try:
        with open(filename, 'wb') as f:
            f.write(audio_data)
    except IOError as e:
        print(f"Failed to save pcm file: {e}")
