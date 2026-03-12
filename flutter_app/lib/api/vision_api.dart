import '../api_client.dart';
import '../models/api_response.dart';

class VisionApiService {
  final ApiClient _client;

  VisionApiService(this._client);

  Future<ApiResponse> analyzeImage({
    required String imagePath,
    String? task,
  }) async {
    return await _client.uploadFile(
      '/api/v1/vision/analyze',
      filePath: imagePath,
      fileField: 'image',
      data: task != null ? {'task': task} : null,
    );
  }

  Future<ApiResponse> detectObjects(String imagePath) async {
    return await _client.uploadFile(
      '/api/v1/vision/detect',
      filePath: imagePath,
      fileField: 'image',
    );
  }

  Future<ApiResponse> recognizeText(String imagePath) async {
    return await _client.uploadFile(
      '/api/v1/vision/ocr',
      filePath: imagePath,
      fileField: 'image',
    );
  }
}
