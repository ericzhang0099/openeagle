class ApiConstants {
  // API版本
  static const String apiVersion = 'v1';

  // 基础路径
  static const String basePath = '/api/$apiVersion';

  // Agent
  static const String agents = '$basePath/agents';
  static String agent(String id) => '$basePath/agents/$id';

  // Session
  static const String sessions = '$basePath/sessions';
  static String session(String id) => '$basePath/sessions/$id';
  static String sessionMessages(String id) => '$basePath/sessions/$id/messages';

  // Chat
  static const String chat = '$basePath/chat';
  static const String chatStream = '$basePath/chat/stream';

  // Vision
  static const String visionAnalyze = '$basePath/vision/analyze';
  static const String visionDetect = '$basePath/vision/detect';
  static const String visionOcr = '$basePath/vision/ocr';

  // Audio
  static const String audioRecognize = '$basePath/audio/recognize';
  static const String audioSynthesize = '$basePath/audio/synthesize';
}

class AppConstants {
  // 应用信息
  static const String appName = 'VisionClaw';
  static const String appVersion = '1.0.0';

  // 超时时间
  static const int connectTimeout = 30000;
  static const int receiveTimeout = 30000;

  // 缓存键
  static const String keyToken = 'token';
  static const String keyUserId = 'user_id';
  static const String keyAgentId = 'agent_id';
  static const String keySessionId = 'session_id';
  static const String keyServerUrl = 'server_url';

  // 音频配置
  static const int audioSampleRate = 16000;
  static const int audioChannels = 1;

  // 图片配置
  static const int imageMaxWidth = 1920;
  static const int imageMaxHeight = 1920;
  static const int imageQuality = 85;
}
