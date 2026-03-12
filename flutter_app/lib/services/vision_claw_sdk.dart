import 'dart:async';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../models/app_config.dart';
import '../models/message.dart';
import '../models/api_response.dart';
import '../api/api_client.dart';
import '../api/agent_api.dart';
import '../api/session_api.dart';
import '../api/chat_api.dart';
import '../api/vision_api.dart';
import '../api/audio_api.dart';

class VisionClawSDK {
  static VisionClawSDK? _instance;
  static VisionClawSDK get instance => _instance!;

  AppConfig _config = AppConfig.defaultConfig();
  ApiClient? _apiClient;
  WebSocketChannel? _wsChannel;
  bool _isConnected = false;
  String? _sessionId;
  String? _agentId;

  // API服务
  late AgentApiService agentApi;
  late SessionApiService sessionApi;
  late ChatApiService chatApi;
  late VisionApiService visionApi;
  late AudioApiService audioApi;

  // 回调
  Function(Message)? onMessageReceived;
  Function(bool)? onConnectionChanged;
  Function(String)? onError;

  bool get isConnected => _isConnected;
  String? get sessionId => _sessionId;

  VisionClawSDK._();

  static Future<void> initialize({AppConfig? config}) async {
    _instance = VisionClawSDK._();
    if (config != null) {
      _instance!._config = config;
    }
    await _instance!._init();
  }

  Future<void> _init() async {
    _apiClient = ApiClient(config: _config);

    // 初始化API服务
    agentApi = AgentApiService(_apiClient!);
    sessionApi = SessionApiService(_apiClient!);
    chatApi = ChatApiService(_apiClient!);
    visionApi = VisionApiService(_apiClient!);
    audioApi = AudioApiService(_apiClient!);
  }

  Future<bool> connect({String? agentId}) async {
    try {
      _agentId = agentId;

      // 如果提供了agentId，先创建session
      if (agentId != null) {
        final sessionResponse = await sessionApi.createSession(agentId: agentId);
        if (sessionResponse.isSuccess) {
          _sessionId = sessionResponse.data['session_id'];
        }
      }

      // 建立WebSocket连接
      final wsUri = Uri.parse(_config.wsUrl);
      _wsChannel = WebSocketChannel.connect(wsUri);

      // 设置监听
      _wsChannel!.stream.listen(
        _onWsMessage,
        onError: _onWsError,
        onDone: _onWsDone,
      );

      _isConnected = true;
      onConnectionChanged?.call(true);
      return true;
    } catch (e) {
      _isConnected = false;
      onConnectionChanged?.call(false);
      onError?.call('连接失败: $e');
      return false;
    }
  }

  void disconnect() {
    _wsChannel?.sink.close();
    _wsChannel = null;
    _isConnected = false;
    _sessionId = null;
    onConnectionChanged?.call(false);
  }

  Future<ApiResponse> sendText(String text) async {
    if (_sessionId != null) {
      return await sessionApi.sendMessage(
        sessionId: _sessionId!,
        content: text,
        type: 'text',
      );
    } else {
      return await chatApi.sendMessage(message: text);
    }
  }

  Future<ApiResponse> sendImage(String imagePath, {String? task}) async {
    if (task != null) {
      return await visionApi.analyzeImage(
        imagePath: imagePath,
        task: task,
      );
    } else {
      return await visionApi.detectObjects(imagePath);
    }
  }

  Future<ApiResponse> sendVoice(String audioPath) async {
    return await audioApi.recognizeAudio(audioPath);
  }

  void _onWsMessage(dynamic message) {
    try {
      final data = message as Map<String, dynamic>;
      final type = data['type'] as String?;

      if (type == 'message') {
        final payload = data['payload'] as Map<String, dynamic>;
        final msg = Message(
          id: payload['message_id'] ?? '',
          type: MessageType.text,
          content: payload['content'] ?? '',
          timestamp: DateTime.now().millisecondsSinceEpoch,
          status: MessageStatus.sent,
          role: MessageRole.assistant,
        );
        onMessageReceived?.call(msg);
      }
    } catch (e) {
      onError?.call('消息解析错误: $e');
    }
  }

  void _onWsError(dynamic error) {
    _isConnected = false;
    onConnectionChanged?.call(false);
    onError?.call('WebSocket错误: $error');
  }

  void _onWsDone() {
    _isConnected = false;
    onConnectionChanged?.call(false);
  }

  void dispose() {
    disconnect();
    _instance = null;
  }
}
