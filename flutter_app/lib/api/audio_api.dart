import '../api_client.dart';
import '../models/api_response.dart';

class AudioApiService {
  final ApiClient _client;

  AudioApiService(this._client);

  Future<ApiResponse> recognizeAudio(String audioPath) async {
    return await _client.uploadFile(
      '/api/v1/audio/recognize',
      filePath: audioPath,
      fileField: 'audio',
    );
  }

  Future<ApiResponse> synthesizeSpeech({
    required String text,
    String? voice,
    double? speed,
  }) async {
    return await _client.post(
      '/api/v1/audio/synthesize',
      data: {
        'text': text,
        'voice': voice ?? 'default',
        'speed': speed ?? 1.0,
      },
    );
  }
}
