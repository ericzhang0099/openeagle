import '../api_client.dart';
import '../models/api_response.dart';

class AgentApiService {
  final ApiClient _client;

  AgentApiService(this._client);

  Future<ApiResponse> createAgent({
    required String name,
    String? type,
    Map<String, dynamic>? config,
  }) async {
    return await _client.post(
      '/api/v1/agents',
      data: {
        'name': name,
        'type': type ?? 'default',
        'config': config ?? {},
      },
    );
  }

  Future<ApiResponse> getAgent(String agentId) async {
    return await _client.get('/api/v1/agents/$agentId');
  }

  Future<ApiResponse> listAgents({int page = 1, int pageSize = 20}) async {
    return await _client.get(
      '/api/v1/agents',
      queryParameters: {
        'page': page,
        'pageSize': pageSize,
      },
    );
  }

  Future<ApiResponse> deleteAgent(String agentId) async {
    return await _client.delete('/api/v1/agents/$agentId');
  }
}
