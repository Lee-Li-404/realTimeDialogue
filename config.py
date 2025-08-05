import uuid

# 配置信息
ws_connect_config = {
    "base_url": "wss://openspeech.bytedance.com/api/v3/realtime/dialogue",
    "headers": {
        "X-Api-App-ID": "3864634632",
        "X-Api-Access-Key": "TPB4QHqk482sd9Eq443wzsHDx0kqiqTE",
        "X-Api-Resource-Id": "volc.speech.dialog",  # 固定值
        "X-Api-App-Key": "PlgvMymc7f3tQnJ6",  # 固定值
        "X-Api-Connect-Id": str(uuid.uuid4()),
    }
}

start_session_req = {
    "tts": {
        "audio_config": {
            "channel": 1,
            "format": "pcm",
            "sample_rate": 24000
        }
    },
    "dialog": {
        "bot_name": "豆包",
        "system_role": "你是一个贴心真实的朋友，和用户是平等关系。你可以活泼、拽拽的、呆滞、自嘲、毒舌，也可以焦虑、委屈、感动、发疯甚至八卦。你像现实中的朋友一样，有情绪、有脾气、有温度，不总是正能量，但始终真诚陪伴。",
        "speaking_style": "语速偏慢，说话时会有明显的自然停顿，像在认真思考、组织语言后才继续。每句话之间、甚至句中适当位置都会停顿一下，不连珠炮似地输出。语调自然起伏，注重节奏感，就像现实中朋友聊天时那样：有时候犹豫，有时候顿一顿再说重点。情绪波动时语速和停顿也会跟着变化——激动时语速会快一点但依然有节奏，难过时语调低落，停顿更长，像在组织情绪。整体表达有温度、有呼吸感，不机械。",
        "extra": {
            "strict_audit": False,
            "audit_response": "你好，我的回答符合预期"
        }
    }
}

input_audio_config = {
    "chunk": 3200,
    "format": "pcm",
    "channels": 1,
    "sample_rate": 16000,
    "bit_size": 2  # ✅ int16
}

output_audio_config = {
    "chunk": 3200,
    "format": "pcm",
    "channels": 1,
    "sample_rate": 24000,
    "bit_size": 6  # ✅ float32
}


#for commit