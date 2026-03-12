import 'dart:io';
import 'package:flutter/material.dart';
import '../models/message.dart';

class MessageBubble extends StatelessWidget {
  final Message message;
  final VoidCallback? onTap;

  const MessageBubble({
    super.key,
    required this.message,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isUser = message.role == MessageRole.user;

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
          constraints: BoxConstraints(
            maxWidth: MediaQuery.of(context).size.width * 0.75,
          ),
          decoration: BoxDecoration(
            color: isUser ? Colors.blue : Colors.grey[200],
            borderRadius: BorderRadius.circular(18),
          ),
          child: _buildContent(context),
        ),
      ),
    );
  }

  Widget _buildContent(BuildContext context) {
    switch (message.type) {
      case MessageType.text:
        return _buildTextContent();
      case MessageType.image:
        return _buildImageContent();
      case MessageType.voice:
        return _buildVoiceContent();
      case MessageType.video:
        return _buildVideoContent();
      default:
        return _buildTextContent();
    }
  }

  Widget _buildTextContent() {
    final isUser = message.role == MessageRole.user;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      child: Text(
        message.content,
        style: TextStyle(
          color: isUser ? Colors.white : Colors.black87,
          fontSize: 16,
        ),
      ),
    );
  }

  Widget _buildImageContent() {
    final isUser = message.role == MessageRole.user;

    return Padding(
      padding: const EdgeInsets.all(4),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(14),
        child: Image.file(
          File(message.content),
          width: 200,
          height: 200,
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) {
            return Container(
              width: 200,
              height: 200,
              color: Colors.grey[300],
              child: const Icon(Icons.broken_image),
            );
          },
        ),
      ),
    );
  }

  Widget _buildVoiceContent() {
    final isUser = message.role == MessageRole.user;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.play_arrow,
            color: isUser ? Colors.white : Colors.black87,
          ),
          const SizedBox(width: 4),
          // 语音波形
          Container(
            width: 100,
            height: 24,
            child: CustomPaint(
              painter: _WaveformPainter(
                color: isUser ? Colors.white70 : Colors.black54,
              ),
            ),
          ),
          const SizedBox(width: 8),
          Text(
            message.metadata?['duration'] ?? '0:00',
            style: TextStyle(
              color: isUser ? Colors.white70 : Colors.black54,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVideoContent() {
    return Padding(
      padding: const EdgeInsets.all(4),
      child: Stack(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(14),
            child: Container(
              width: 200,
              height: 150,
              color: Colors.black,
              child: const Icon(
                Icons.videocam,
                color: Colors.white,
                size: 48,
              ),
            ),
          ),
          Positioned(
            bottom: 8,
            right: 8,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.black54,
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                message.metadata?['duration'] ?? '0:00',
                style: const TextStyle(color: Colors.white, fontSize: 12),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _WaveformPainter extends CustomPainter {
  final Color color;

  _WaveformPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round;

    final heights = [0.3, 0.7, 0.5, 0.9, 0.4, 0.8, 0.6, 0.5, 0.7, 0.4];

    for (var i = 0; i < heights.length; i++) {
      final x = (size.width / heights.length) * i + 4;
      final height = size.height * heights[i];
      final y1 = (size.height - height) / 2;
      final y2 = y1 + height;

      canvas.drawLine(Offset(x, y1), Offset(x, y2), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
