# VisionClaw Audio Service

基于 FastAPI + Whisper + Piper 的语音服务模块，提供语音识别(STT)和语音合成(TTS)功能。

## 技术栈

- Python 3.10+
- FastAPI - Web框架
- Whisper - 语音识别
- Piper - 语音合成

## 项目结构

```
audio_service/
├── main.py              # FastAPI入口
├── requirements.txt     # 依赖文件
├── core/
│   ├── __init__.py
│   └── config.py        # 配置管理
├── api/
│   ├── __init__.py
│   └── audio.py         # 音频路由
├── services/
│   ├── __init__.py
│   ├── stt_service.py   # 语音识别服务
│   └── tts_service.py   # 语音合成服务
├── models/
│   ├── __init__.py
│   └── schemas.py       # Pydantic模型
└── utils/
    ├── __init__.py
    └── helpers.py       # 工具函数
```

## 快速开始

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 运行服务
```bash
python main.py
```

3. 访问API文档
```
http://localhost:8000/docs
```

## API接口

- `POST /api/v1/audio/stt` - 语音识别
- `POST /api/v1/audio/tts` - 语音合成
