import 'package:flutter/material.dart';

class DateDivider extends StatelessWidget {
  final DateTime date;

  const DateDivider({super.key, required this.date});

  String _getDateString() {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final yesterday = today.subtract(const Duration(days: 1));
    final messageDate = DateTime(date.year, date.month, date.day);

    if (messageDate == today) {
      return '今天';
    } else if (messageDate == yesterday) {
      return '昨天';
    } else {
      return '${date.month}月${date.day}日';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Center(
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
          decoration: BoxDecoration(
            color: Colors.grey[200],
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            _getDateString(),
            style: TextStyle(
              color: Colors.grey[600],
              fontSize: 12,
            ),
          ),
        ),
      ),
    );
  }
}

class TimeSeparator extends StatelessWidget {
  final DateTime time;

  const TimeSeparator({super.key, required this.time});

  String _formatTime() {
    final hour = time.hour.toString().padLeft(2, '0');
    final minute = time.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Text(
        _formatTime(),
        style: TextStyle(
          color: Colors.grey[400],
          fontSize: 11,
        ),
      ),
    );
  }
}

class MessageStatusIcon extends StatelessWidget {
  final String status;

  const MessageStatusIcon({super.key, required this.status});

  @override
  Widget build(BuildContext context) {
    IconData icon;
    Color color;

    switch (status) {
      case 'sending':
        icon = Icons.access_time;
        color = Colors.grey;
        break;
      case 'sent':
        icon = Icons.check;
        color = Colors.grey;
        break;
      case 'delivered':
        icon = Icons.done_all;
        color = Colors.grey;
        break;
      case 'read':
        icon = Icons.done_all;
        color = Colors.blue;
        break;
      case 'error':
        icon = Icons.error_outline;
        color = Colors.red;
        break;
      default:
        icon = Icons.check;
        color = Colors.grey;
    }

    return Icon(icon, size: 14, color: color);
  }
}

class AvatarWidget extends StatelessWidget {
  final String? imageUrl;
  final String name;
  final double size;

  const AvatarWidget({
    super.key,
    this.imageUrl,
    required this.name,
    this.size = 40,
  });

  String _getInitials() {
    if (name.isEmpty) return '?';
    return name[0].toUpperCase();
  }

  @override
  Widget build(BuildContext context) {
    if (imageUrl != null && imageUrl!.isNotEmpty) {
      return ClipOval(
        child: Image.network(
          imageUrl!,
          width: size,
          height: size,
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) {
            return _buildDefaultAvatar();
          },
        ),
      );
    }
    return _buildDefaultAvatar();
  }

  Widget _buildDefaultAvatar() {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: Colors.blue,
        shape: BoxShape.circle,
      ),
      child: Center(
        child: Text(
          _getInitials(),
          style: TextStyle(
            color: Colors.white,
            fontSize: size * 0.4,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
}

class UnreadBadge extends StatelessWidget {
  final int count;

  const UnreadBadge({super.key, required this.count});

  @override
  Widget build(BuildContext context) {
    if (count <= 0) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: Colors.red,
        borderRadius: BorderRadius.circular(10),
      ),
      constraints: const BoxConstraints(minWidth: 18),
      child: Text(
        count > 99 ? '99+' : count.toString(),
        style: const TextStyle(
          color: Colors.white,
          fontSize: 10,
          fontWeight: FontWeight.bold,
        ),
        textAlign: TextAlign.center,
      ),
    );
  }
}
