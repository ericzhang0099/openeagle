"""
API测试脚本 - 测试语音服务接口
"""

import httpx
import base64
import time

BASE_URL = "http://localhost:8000/api/v1"


def test_health():
    """测试健康检查"""
    response = httpx.get(f"{BASE_URL.replace('/api/v1', '')}/health")
    print(f"Health Check: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✅ Health check passed\n")


def test_audio_info():
    """测试音频服务信息"""
    response = httpx.get(f"{BASE_URL}/audio/info")
    print(f"Audio Info: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["code"] == 0
    print("✅ Audio info passed\n")


def test_tts():
    """测试语音合成"""
    response = httpx.post(
        f"{BASE_URL}/audio/synthesize",
        json={
            "text": "你好，这是测试",
            "voice": "zh_CN",
            "speed": 1.0
        }
    )
    print(f"TTS: {response.status_code}")
    result = response.json()
    print(f"Response code: {result['code']}")
    print(f"Has audio data: {'audio' in result['data']}")
    assert response.status_code == 200
    assert result["code"] == 0
    assert "audio" in result["data"]
    print("✅ TTS passed\n")


def test_stt():
    """测试语音识别（需要音频文件）"""
    # 创建测试用的空WAV文件
    test_wav = b"RIFF\x26\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00" \
                b"\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x02\x00\x00\x00\x00\x00"
    
    response = httpx.post(
        f"{BASE_URL}/audio/recognize",
        files={"audio": ("test.wav", test_wav, "audio/wav")},
        data={"language": "zh"}
    )
    print(f"STT: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    assert response.status_code == 200
    assert result["code"] == 0
    assert "text" in result["data"]
    print("✅ STT passed\n")


if __name__ == "__main__":
    print("=" * 50)
    print("VisionClaw Audio Service - API Tests")
    print("=" * 50)
    print()
    
    try:
        test_health()
        test_audio_info()
        test_tts()
        test_stt()
        print("=" * 50)
        print("✅ All tests passed!")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("Make sure the server is running: python main.py")
