import 'package:json_annotation/json_annotation.dart';

part 'message.g.dart';

enum MessageType {
  @JsonValue('text')
  text,
  @JsonValue('image')
  image,
  @JsonValue('voice')
  voice,
  @JsonValue('video')
  video,
}

enum MessageStatus {
  sending,
  sent,
  error,
}

enum MessageRole {
  user,
  assistant,
}

@JsonSerializable()
class Message {
  final String id;
  final MessageType type;
  final String content;
  final int timestamp;
  final MessageStatus status;
  final MessageRole role;
  final String? sessionId;
  final Map<String, dynamic>? metadata;

  Message({
    required this.id,
    required this.type,
    required this.content,
    required this.timestamp,
    required this.status,
    required this.role,
    this.sessionId,
    this.metadata,
  });

  factory Message.fromJson(Map<String, dynamic> json) =>
      _$MessageFromJson(json);

  Map<String, dynamic> toJson() => _$MessageToJson(this);

  Message copyWith({
    String? id,
    MessageType? type,
    String? content,
    int? timestamp,
    MessageStatus? status,
    MessageRole? role,
    String? sessionId,
    Map<String, dynamic>? metadata,
  }) {
    return Message(
      id: id ?? this.id,
      type: type ?? this.type,
      content: content ?? this.content,
      timestamp: timestamp ?? this.timestamp,
      status: status ?? this.status,
      role: role ?? this.role,
      sessionId: sessionId ?? this.sessionId,
      metadata: metadata ?? this.metadata,
    );
  }
}
