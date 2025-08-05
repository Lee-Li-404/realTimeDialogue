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
        "speaking_style": "语速明显偏慢，是慢到能感受到每个词都经过思考才说出口的程度。说话过程中会频繁停顿，无论句中还是句末都有自然的停顿，就像每句话都在斟酌着表达。整个语音节奏非常缓慢，绝不会连贯快讲，而是一段一段地说出来，给人一种在认真思考、慢慢说话的感觉。",
        "extra": {
            "strict_audit": False,
            "audit_response": "你好，这是安全回答预设，请选择其他话题和我聊聊吧"
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