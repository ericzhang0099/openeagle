import '../api_client.dart';
import '../models/api_response.dart';

class SessionApiService {
  final ApiClient _client;

  SessionApiService(this._client);

  Future<ApiResponse> createSession({required String agentId}) async {
    return await _client.post(
      '/api/v1/sessions',
      data: {
        'agent_id': agentId,
      },
    );
  }

  Future<ApiResponse> getSession(String sessionId) async {
    return await _client.get('/api/v1/sessions/$sessionId');
  }

  Future<ApiResponse> sendMessage({
    required String sessionId,
    required String content,
    String type = 'text',
  }) async {
    return await _client.post(
      '/api/v1/sessions/$sessionId/messages',
      data: {
        'content': content,
        'type': type,
      },
    );
  }

  Future<ApiResponse> endSession(String sessionId) async {
    return await _client.delete('/api/v1/sessions/$sessionId');
  }

  Future<ApiResponse> getMessages(
    String sessionId, {
    int page = 1,
    int pageSize = 50,
  }) async {
    return await _client.get(
      '/api/v1/sessions/$sessionId/messages',
      queryParameters: {
        'page': page,
        'pageSize': pageSize,
      },
    );
  }
}
