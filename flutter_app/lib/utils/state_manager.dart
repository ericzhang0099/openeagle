import 'package:flutter/material.dart';

class SessionManager {
  static final SessionManager _instance = SessionManager._internal();
  factory SessionManager() => _instance;
  SessionManager._internal();

  String? _currentSessionId;
  String? _currentAgentId;
  DateTime? _sessionStartTime;
  bool _isActive = false;

  String? get currentSessionId => _currentSessionId;
  String? get currentAgentId => _currentAgentId;
  bool get isActive => _isActive;
  DateTime? get sessionStartTime => _sessionStartTime;

  Duration get sessionDuration {
    if (_sessionStartTime == null) return Duration.zero;
    return DateTime.now().difference(_sessionStartTime!);
  }

  void startSession({required String sessionId, required String agentId}) {
    _currentSessionId = sessionId;
    _currentAgentId = agentId;
    _sessionStartTime = DateTime.now();
    _isActive = true;
  }

  void endSession() {
    _currentSessionId = null;
    _currentAgentId = null;
    _sessionStartTime = null;
    _isActive = false;
  }

  bool get hasActiveSession => _isActive && _currentSessionId != null;
}

// 用户管理
class UserManager {
  static final UserManager _instance = UserManager._internal();
  factory UserManager() => _instance;
  UserManager._internal();

  String? _userId;
  String? _userName;
  String? _avatarUrl;
  Map<String, dynamic>? _extraInfo;

  String? get userId => _userId;
  String? get userName => _userName;
  String? get avatarUrl => _avatarUrl;
  Map<String, dynamic>? get extraInfo => _extraInfo;
  bool get isLoggedIn => _userId != null;

  void login({
    required String userId,
    String? userName,
    String? avatarUrl,
    Map<String, dynamic>? extraInfo,
  }) {
    _userId = userId;
    _userName = userName;
    _avatarUrl = avatarUrl;
    _extraInfo = extraInfo;
  }

  void logout() {
    _userId = null;
    _userName = null;
    _avatarUrl = null;
    _extraInfo = null;
  }

  void updateUserName(String userName) {
    _userName = userName;
  }

  void updateAvatar(String avatarUrl) {
    _avatarUrl = avatarUrl;
  }
}

// 应用状态管理
class AppStateManager {
  static final AppStateManager _instance = AppStateManager._internal();
  factory AppStateManager() => _instance;
  AppStateManager._internal();

  bool _isDarkMode = false;
  String _language = 'zh_CN';
  bool _isFirstLaunch = true;
  bool _isInitialized = false;

  bool get isDarkMode => _isDarkMode;
  String get language => _language;
  bool get isFirstLaunch => _isFirstLaunch;
  bool get isInitialized => _isInitialized;

  void setDarkMode(bool value) {
    _isDarkMode = value;
  }

  void setLanguage(String value) {
    _language = value;
  }

  void setFirstLaunch(bool value) {
    _isFirstLaunch = value;
  }

  void setInitialized(bool value) {
    _isInitialized = value;
  }

  void toggleDarkMode() {
    _isDarkMode = !_isDarkMode;
  }
}

// 主题管理
class ThemeManager {
  static ThemeData get lightTheme => ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
  );

  static ThemeData get darkTheme => ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue, brightness: Brightness.dark),
  );
}
