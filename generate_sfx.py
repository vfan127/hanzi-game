#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用百度TTS生成游戏提示音 - 带认证"""

import os
import base64
import json
import requests
import hashlib
import time

# 百度认证配置
API_KEY = "Exz0VO2k7Fz3aHlpQi8WJF7Z"
SECRET_KEY = "vK8eCZy95uyUsXCJABKIkHpaFNuCkJXS"

# 百度TTS API
BAIDU_TTS_URL = "https://tsn.baidu.com/text2audio"

# Token获取URL
TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"

# 需要生成的语音文本
TEXTS = {
    # 答对鼓励
    "correct_1": "太棒了！",
    "correct_2": "真厉害！",
    "correct_3": "你真聪明！",
    "correct_4": "继续保持！",
    "correct_5": "太优秀了！",
    "correct_6": "完美！",
    # 答错鼓励
    "wrong_1": "没关系，再试一次！",
    "wrong_2": "加油，你可以的！",
    "wrong_3": "别灰心，继续努力！",
    "wrong_4": "下一次一定行！",
    # 庆祝
    "celebrate": "恭喜过关！你真棒！"
}

def get_access_token():
    """获取百度Access Token"""
    params = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": SECRET_KEY
    }

    try:
        response = requests.get(TOKEN_URL, params=params, timeout=30)
        result = response.json()

        if "access_token" in result:
            print(f"[OK] Got access token")
            return result["access_token"]
        else:
            print(f"[ERR] Failed to get token: {result}")
            return None
    except Exception as e:
        print(f"[ERR] Token request failed: {e}")
        return None

def call_baidu_tts(text, output_file, access_token):
    """调用百度TTS API生成语音"""
    params = {
        "tex": text,
        "tok": access_token,
        "per": 0,      # 度小美（女声）
        "spd": 5,      # 语速
        "pit": 5,      # 音调
        "vol": 5,      # 音量
        "aue": 3,      # MP3格式
        "cuid": "hanzi_game_sfx",
        "lan": "zh",
        "ctp": 1,
    }

    try:
        response = requests.get(BAIDU_TTS_URL, params=params, timeout=30)
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'audio' in content_type or len(response.content) > 1000:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print(f"[OK] {text} -> {os.path.basename(output_file)}")
                return True
            else:
                print(f"[ERR] API error: {response.text[:200]}")
                return False
        else:
            print(f"[ERR] HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERR] Request failed: {e}")
        return False

def main():
    print("[SFX] Starting to generate game sound effects with Baidu TTS...")

    # 获取access token
    print("[...] Getting access token...")
    access_token = get_access_token()
    if not access_token:
        print("[ERR] Cannot proceed without access token")
        return

    # 创建输出目录
    output_dir = os.path.join(os.path.dirname(__file__), "sfx")
    os.makedirs(output_dir, exist_ok=True)
    print(f"[DIR] Output: {output_dir}")

    # 生成所有语音
    results = {}
    for key, text in TEXTS.items():
        output_file = os.path.join(output_dir, f"{key}.mp3")
        if call_baidu_tts(text, output_file, access_token):
            results[key] = text
        time.sleep(0.3)  # 避免请求过快

    print()
    print(f"[DONE] Generated {len(results)} audio files")

    # 生成音频清单JSON
    audio_list = {}
    for key, text in TEXTS.items():
        mp3_file = f"sfx/{key}.mp3"
        if os.path.exists(os.path.join(os.path.dirname(__file__), mp3_file)):
            audio_list[key] = {
                "file": mp3_file,
                "text": text
            }

    with open("sfx-audio-list.json", "w", encoding="utf-8") as f:
        json.dump(audio_list, f, ensure_ascii=False, indent=2)

    print(f"[JSON] Audio list saved: sfx-audio-list.json")

if __name__ == "__main__":
    main()
