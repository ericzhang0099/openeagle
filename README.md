# VisionClaw Vision Service

视觉服务模块 - 提供图像分析、目标检测、OCR文字识别能力

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload

# 访问文档
http://localhost:8000/docs
```

## API接口

- `POST /api/v1/vision/analyze` - 图像分析
- `POST /api/v1/vision/detect` - 目标检测  
- `POST /api/v1/vision/ocr` - OCR文字识别

## Docker部署

```bash
docker build -t vision-service .
docker run -p 8000:8000 vision-service
```
