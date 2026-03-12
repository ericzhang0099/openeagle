import '../api_client.dart';
import '../models/api_response.dart';

class ChatApiService {
  final ApiClient _client;

  ChatApiService(this._client);

  Future<ApiResponse> sendMessage({
    required String message,
    Map<String, dynamic>? context,
  }) async {
    return await _client.post(
      '/api/v1/chat',
      data: {
        'message': message,
        'context': context ?? {},
      },
    );
  }

  Stream<ApiResponse> sendStreamMessage(String message) async* {
    // 流式消息处理
    final uri = Uri.parse('${_client.config.baseUrl}/api/v1/chat/stream')
        .replace(queryParameters: {'message': message});

    // TODO: 实现SSE流式读取
    yield ApiResponse.success({'content': ''});
  }
}
