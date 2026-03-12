# VisionClaw Backend

VisionClaw 后端 API 服务

## 技术栈

- FastAPI
- PostgreSQL (异步)
- Redis
- Python 3.10+

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

创建 `.env` 文件：

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/vision_claw
REDIS_URL=redis://localhost:6379/0
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

### 3. 启动服务

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. 访问文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 接口

### Agent

- `POST /api/v1/agents` - 创建Agent
- `GET /api/v1/agents` - 获取Agent列表
- `GET /api/v1/agents/{id}` - 获取Agent详情
- `PUT /api/v1/agents/{id}` - 更新Agent
- `DELETE /api/v1/agents/{id}` - 删除Agent

### Session

- `POST /api/v1/sessions` - 创建会话
- `GET /api/v1/sessions/{id}` - 获取会话
- `POST /api/v1/sessions/{id}/messages` - 发送消息
- `GET /api/v1/sessions/{id}/messages` - 获取消息列表
- `DELETE /api/v1/sessions/{id}` - 结束会话

### Chat

- `POST /api/v1/chat` - 单轮对话
- `GET /api/v1/chat/stream` - 流式对话

### Vision

- `POST /api/v1/vision/analyze` - 图像分析
- `POST /api/v1/vision/detect` - 目标检测
- `POST /api/v1/vision/ocr` - 文字识别

### Audio

- `POST /api/v1/audio/recognize` - 语音识别
- `POST /api/v1/audio/synthesize` - 语音合成
- `POST /api/v1/audio/events` - 声音事件检测

## 项目结构

```
backend/
├── app/
│   ├── api/          # API路由
│   ├── core/         # 核心配置
│   ├── models/      # 数据库模型
│   ├── schemas/     # Pydantic模型
│   ├── services/    # 业务逻辑
│   └── main.py      # 应用入口
├── requirements.txt
└── README.md
```
