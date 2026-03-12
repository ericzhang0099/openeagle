// 事件总线 - 用于组件间通信
import 'dart:async';

class EventBus {
  static final EventBus _instance = EventBus._internal();
  factory EventBus() => _instance;
  EventBus._internal();

  final _eventController = StreamController.broadcast();

  // 监听事件
  Stream<T> on<T>() {
    return _eventController.stream.where((event) => event is T).map((event) => event as T);
  }

  // 发送事件
  void fire(dynamic event) {
    _eventController.add(event);
  }

  // 关闭
  void dispose() {
    _eventController.close();
  }
}

// 事件定义
abstract class AppEvent {}

class ConnectionChangedEvent extends AppEvent {
  final bool isConnected;
  ConnectionChangedEvent(this.isConnected);
}

class MessageReceivedEvent extends AppEvent {
  final dynamic message;
  MessageReceivedEvent(this.message);
}

class MessageSentEvent extends AppEvent {
  final dynamic message;
  MessageSentEvent(this.message);
}

class ErrorEvent extends AppEvent {
  final String error;
  ErrorEvent(this.error);
}

class LoginSuccessEvent extends AppEvent {
  final dynamic user;
  LoginSuccessEvent(this.user);
}

class LogoutEvent extends AppEvent {}

class ThemeChangedEvent extends AppEvent {
  final bool isDark;
  ThemeChangedEvent(this.isDark);
}

class LanguageChangedEvent extends AppEvent {
  final String language;
  LanguageChangedEvent(this.language);
}
