# VisionClaw Flutter App

VisionClaw 移动端 Flutter 应用

## 功能

- 文字聊天
- 语音输入
- 图像识别
- 视频通话
- 摄像头控制

## 快速开始

### 安装依赖

```bash
flutter pub get
```

### 运行

```bash
flutter run
```

### 构建

```bash
# Debug
flutter build apk --debug

# Release
flutter build apk --release
```

## 项目结构

```
lib/
├── api/              # API接口
├── constants/        # 常量定义
├── models/           # 数据模型
├── screens/          # 页面
├── services/         # 服务
├── utils/            # 工具类
├── widgets/          # 组件
└── main.dart         # 入口
```

## 配置

修改 `lib/models/app_config.dart` 中的默认配置：

```dart
AppConfig(
  baseUrl: 'http://your-server:8000',
  wsUrl: 'ws://your-server:8000',
)
```

## API

详细API定义见项目文档。
