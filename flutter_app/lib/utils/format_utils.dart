import 'dart:convert';
import 'package:crypto/crypto.dart';

class EncryptionUtils {
  // MD5加密
  static String md5(String input) {
    return md5.convert(utf8.encode(input)).toString();
  }

  // SHA1加密
  static String sha1(String input) {
    return sha1.convert(utf8.encode(input)).toString();
  }

  // SHA256加密
  static String sha256(String input) {
    return sha256.convert(utf8.encode(input)).toString();
  }

  // Base64编码
  static String base64Encode(String input) {
    return base64Encode(utf8.encode(input));
  }

  // Base64解码
  static String base64Decode(String input) {
    return utf8.decode(base64Decode(input));
  }

  // URL编码
  static String urlEncode(String input) {
    return Uri.encodeComponent(input);
  }

  // URL解码
  static String urlDecode(String input) {
    return Uri.decodeComponent(input);
  }
}

class DeviceUtils {
  // 获取设备信息
  static String getDeviceInfo() {
    // TODO: 实现设备信息获取
    return 'Unknown Device';
  }

  // 获取设备ID
  static String getDeviceId() {
    // TODO: 实现设备ID获取
    return '';
  }

  // 获取操作系统版本
  static String getOsVersion() {
    // TODO: 实现OS版本获取
    return 'Unknown';
  }

  // 获取App版本
  static String getAppVersion() {
    return '1.0.0';
  }

  // 获取构建号
  static String getBuildNumber() {
    return '1';
  }

  // 检查是否为模拟器
  static bool isSimulator() {
    // TODO: 实现模拟器检测
    return false;
  }

  // 检查是否有网络
  static Future<bool> hasNetwork() async {
    // TODO: 实现网络检测
    return true;
  }
}

class DateTimeUtils {
  // 格式化时间
  static String formatTime(DateTime dateTime) {
    final hour = dateTime.hour.toString().padLeft(2, '0');
    final minute = dateTime.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }

  // 格式化日期
  static String formatDate(DateTime dateTime) {
    final year = dateTime.year;
    final month = dateTime.month.toString().padLeft(2, '0');
    final day = dateTime.day.toString().padLeft(2, '0');
    return '$year-$month-$day';
  }

  // 格式化日期时间
  static String formatDateTime(DateTime dateTime) {
    return '${formatDate(dateTime)} ${formatTime(dateTime)}';
  }

  // 相对时间
  static String relativeTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inSeconds < 60) {
      return '刚刚';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}分钟前';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}小时前';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}天前';
    } else {
      return formatDate(dateTime);
    }
  }

  // 是否是今天
  static bool isToday(DateTime dateTime) {
    final now = DateTime.now();
    return dateTime.year == now.year &&
        dateTime.month == now.month &&
        dateTime.day == now.day;
  }

  // 是否是昨天
  static bool isYesterday(DateTime dateTime) {
    final yesterday = DateTime.now().subtract(const Duration(days: 1));
    return dateTime.year == yesterday.year &&
        dateTime.month == yesterday.month &&
        dateTime.day == yesterday.day;
  }
}

class NumberUtils {
  // 格式化数字
  static String formatNumber(int number) {
    if (number < 1000) {
      return number.toString();
    } else if (number < 10000) {
      return '${(number / 1000).toStringAsFixed(1)}K';
    } else if (number < 1000000) {
      return '${(number / 10000).toStringAsFixed(1)}W';
    } else {
      return '${(number / 1000000).toStringAsFixed(1)}M';
    }
  }

  // 格式化文件大小
  static String formatFileSize(int bytes) {
    if (bytes < 1024) {
      return '$bytes B';
    } else if (bytes < 1024 * 1024) {
      return '${(bytes / 1024).toStringAsFixed(1)} KB';
    } else if (bytes < 1024 * 1024 * 1024) {
      return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    } else {
      return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(1)} GB';
    }
  }

  // 手机号格式化
  static String formatPhone(String phone) {
    if (phone.length == 11) {
      return '${phone.substring(0, 3)}****${phone.substring(7)}';
    }
    return phone;
  }

  // 身份证号格式化
  static String formatIdCard(String idCard) {
    if (idCard.length == 18) {
      return '${idCard.substring(0, 6)}********${idCard.substring(14)}';
    }
    return idCard;
  }
}

class CollectionUtils {
  // 判断列表是否为空
  static bool isEmpty(List? list) {
    return list == null || list.isEmpty;
  }

  // 判断列表是否不为空
  static bool isNotEmpty(List? list) {
    return !isEmpty(list);
  }

  // 获取列表第一个元素
  static dynamic firstOrNull(List? list) {
    if (isEmpty(list)) return null;
    return list!.first;
  }

  // 获取列表最后一个元素
  static dynamic lastOrNull(List? list) {
    if (isEmpty(list)) return null;
    return list!.last;
  }
}
