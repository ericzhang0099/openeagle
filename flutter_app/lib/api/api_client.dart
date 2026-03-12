import 'package:dio/dio.dart';
import '../models/api_response.dart';
import '../models/app_config.dart';

class ApiClient {
  late final Dio _dio;
  final AppConfig config;

  ApiClient({required this.config}) {
    _dio = Dio(
      BaseOptions(
        baseUrl: config.baseUrl,
        connectTimeout: Duration(milliseconds: config.timeout),
        receiveTimeout: Duration(milliseconds: config.timeout),
        headers: {
          'Content-Type': 'application/json',
        },
      ),
    );

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          // TODO: 添加认证token
          return handler.next(options);
        },
        onResponse: (response, handler) {
          return handler.next(response);
        },
        onError: (error, handler) {
          return handler.next(error);
        },
      ),
    );
  }

  Future<ApiResponse> get(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      final response = await _dio.get(path, queryParameters: queryParameters);
      return ApiResponse.fromJson(response.data);
    } on DioException catch (e) {
      return _handleError(e);
    }
  }

  Future<ApiResponse> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      final response = await _dio.post(
        path,
        data: data,
        queryParameters: queryParameters,
      );
      return ApiResponse.fromJson(response.data);
    } on DioException catch (e) {
      return _handleError(e);
    }
  }

  Future<ApiResponse> put(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      final response = await _dio.put(
        path,
        data: data,
        queryParameters: queryParameters,
      );
      return ApiResponse.fromJson(response.data);
    } on DioException catch (e) {
      return _handleError(e);
    }
  }

  Future<ApiResponse> delete(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      final response = await _dio.delete(path, queryParameters: queryParameters);
      return ApiResponse.fromJson(response.data);
    } on DioException catch (e) {
      return _handleError(e);
    }
  }

  Future<ApiResponse> uploadFile(
    String path, {
    required String filePath,
    required String fileField,
    Map<String, dynamic>? data,
  }) async {
    try {
      final formData = FormData.fromMap({
        ...?data,
        fileField: await MultipartFile.fromFile(filePath),
      });

      final response = await _dio.post(
        path,
        data: formData,
        options: Options(
          contentType: 'multipart/form-data',
        ),
      );
      return ApiResponse.fromJson(response.data);
    } on DioException catch (e) {
      return _handleError(e);
    }
  }

  ApiResponse _handleError(DioException e) {
    int code = ErrorCode.serverError;
    String message = '网络错误';

    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        message = '连接超时';
        break;
      case DioExceptionType.badResponse:
        code = e.response?.statusCode ?? ErrorCode.serverError;
        message = e.response?.data?['message'] ?? '服务器错误';
        break;
      case DioExceptionType.cancel:
        message = '请求取消';
        break;
      case DioExceptionType.connectionError:
        message = '网络连接失败';
        break;
      default:
        message = e.message ?? '未知错误';
    }

    return ApiResponse.error(code, message);
  }
}
