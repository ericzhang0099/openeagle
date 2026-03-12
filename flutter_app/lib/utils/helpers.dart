import 'package:flutter/material.dart';

class Logger {
  static const String _tag = 'VisionClaw';
  
  static void debug(String message, {String? tag}) {
    _log('DEBUG', message, tag: tag);
  }
  
  static void info(String message, {String? tag}) {
    _log('INFO', message, tag: tag);
  }
  
  static void warning(String message, {String? tag}) {
    _log('WARNING', message, tag: tag);
  }
  
  static void error(String message, {String? tag, Object? error, StackTrace? stackTrace}) {
    _log('ERROR', message, tag: tag);
    if (error != null) {
      debug('Error: $error', tag: tag);
    }
    if (stackTrace != null) {
      debug('StackTrace: $stackTrace', tag: tag);
    }
  }
  
  static void _log(String level, String message, {String? tag}) {
    final timestamp = DateTime.now().toIso8601String();
    final tagStr = tag ?? _tag;
    // 实际使用可以替换为 print 或日志框架
    print('[$timestamp][$level][$tagStr] $message');
  }
}

class DateUtils {
  static String formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final yesterday = today.subtract(const Duration(days: 1));
    final date = DateTime(dateTime.year, dateTime.month, dateTime.day);

    if (date == today) {
      return '今天 ${_formatTime(dateTime)}';
    } else if (date == yesterday) {
      return '昨天 ${_formatTime(dateTime)}';
    } else if (now.difference(dateTime).inDays < 7) {
      return '${_getWeekday(dateTime.weekday)} ${_formatTime(dateTime)}';
    } else {
      return '${dateTime.month}月${dateTime.day}日 ${_formatTime(dateTime)}';
    }
  }

  static String _formatTime(DateTime dateTime) {
    final hour = dateTime.hour.toString().padLeft(2, '0');
    final minute = dateTime.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }

  static String _getWeekday(int weekday) {
    const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    return weekdays[weekday - 1];
  }

  static String formatDuration(Duration duration) {
    final minutes = duration.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds = duration.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$minutes:$seconds';
  }
}

class StringUtils {
  static bool isEmpty(String? str) {
    return str == null || str.isEmpty;
  }

  static bool isNotEmpty(String? str) {
    return !isEmpty(str);
  }

  static String truncate(String str, int maxLength, {String suffix = '...'}) {
    if (str.length <= maxLength) return str;
    return '${str.substring(0, maxLength - suffix.length)}$suffix';
  }

  static String capitalize(String str) {
    if (str.isEmpty) return str;
    return str[0].toUpperCase() + str.substring(1);
  }
}

class FileUtils {
  static String getFileExtension(String path) {
    final lastDot = path.lastIndexOf('.');
    if (lastDot == -1) return '';
    return path.substring(lastDot + 1).toLowerCase();
  }

  static String getFileName(String path) {
    final lastSlash = path.lastIndexOf('/');
    if (lastSlash == -1) return path;
    return path.substring(lastSlash + 1);
  }

  static String formatFileSize(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    if (bytes < 1024 * 1024 * 1024) {
      return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    }
    return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(1)} GB';
  }
}

class Validators {
  static bool isValidUrl(String url) {
    try {
      final uri = Uri.parse(url);
      return uri.hasScheme && (uri.scheme == 'http' || uri.scheme == 'https');
    } catch (e) {
      return false;
    }
  }

  static bool isValidEmail(String email) {
    return RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(email);
  }

  static bool isValidPhone(String phone) {
    return RegExp(r'^1[3-9]\d{9}$').hasMatch(phone);
  }
}
