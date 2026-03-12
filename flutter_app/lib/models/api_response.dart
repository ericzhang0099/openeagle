import 'package:json_annotation/json_annotation.dart';

part 'api_response.g.dart';

@JsonSerializable()
class ApiResponse {
  final int code;
  final String message;
  final dynamic data;
  final int timestamp;

  ApiResponse({
    required this.code,
    required this.message,
    this.data,
    required this.timestamp,
  });

  factory ApiResponse.fromJson(Map<String, dynamic> json) =>
      _$ApiResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ApiResponseToJson(this);

  bool get isSuccess => code == 0;

  static ApiResponse success(dynamic data, {String message = 'success'}) {
    return ApiResponse(
      code: 0,
      message: message,
      data: data,
      timestamp: DateTime.now().millisecondsSinceEpoch,
    );
  }

  static ApiResponse error(int code, String message) {
    return ApiResponse(
      code: code,
      message: message,
      data: null,
      timestamp: DateTime.now().millisecondsSinceEpoch,
    );
  }
}

class ErrorCode {
  static const int success = 0;
  static const int paramError = 1000;
  static const int authFailed = 1001;
  static const int permissionDenied = 1002;
  static const int notFound = 2000;
  static const int serverError = 3000;
  static const int thirdPartyError = 4000;
}
