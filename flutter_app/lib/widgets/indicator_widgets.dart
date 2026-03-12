import 'package:flutter/material.dart';

class ConnectionStatusWidget extends StatelessWidget {
  final bool isConnected;
  final String? serverUrl;
  final VoidCallback? onConnect;
  final VoidCallback? onDisconnect;

  const ConnectionStatusWidget({
    super.key,
    required this.isConnected,
    this.serverUrl,
    this.onConnect,
    this.onDisconnect,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: isConnected ? Colors.green[50] : Colors.red[50],
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: isConnected ? Colors.green : Colors.red,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 8),
          Text(
            isConnected ? '已连接' : '未连接',
            style: TextStyle(
              color: isConnected ? Colors.green[700] : Colors.red[700],
              fontSize: 12,
            ),
          ),
          if (serverUrl != null && isConnected) ...[
            const SizedBox(width: 8),
            GestureDetector(
              onTap: onDisconnect,
              child: Icon(
                Icons.close,
                size: 14,
                color: Colors.grey[600],
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class VoiceInputIndicator extends StatefulWidget {
  final int seconds;
  final VoidCallback? onCancel;

  const VoiceInputIndicator({
    super.key,
    required this.seconds,
    this.onCancel,
  });

  @override
  State<VoiceInputIndicator> createState() => _VoiceInputIndicatorState();
}

class _VoiceInputIndicatorState extends State<VoiceInputIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 500),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  String _formatTime(int seconds) {
    final minutes = seconds ~/ 60;
    final secs = seconds % 60;
    return '$minutes:${secs.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.red[50],
        borderRadius: BorderRadius.circular(24),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // 录音动画
          AnimatedBuilder(
            animation: _controller,
            builder: (context, child) {
              return Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.5 + _controller.value * 0.5),
                  shape: BoxShape.circle,
                ),
              );
            },
          ),
          const SizedBox(width: 12),

          // 录音时间
          Text(
            _formatTime(widget.seconds),
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(width: 12),

          // 取消按钮
          GestureDetector(
            onTap: widget.onCancel,
            child: Container(
              padding: const EdgeInsets.all(4),
              decoration: BoxDecoration(
                color: Colors.grey[300],
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.close, size: 16),
            ),
          ),
        ],
      ),
    );
  }
}

class TypingIndicator extends StatefulWidget {
  const TypingIndicator({super.key});

  @override
  State<TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<TypingIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: List.generate(3, (index) {
          return AnimatedBuilder(
            animation: _controller,
            builder: (context, child) {
              final delay = index * 0.2;
              final value = (_controller.value + delay) % 1.0;
              return Container(
                margin: const EdgeInsets.symmetric(horizontal: 2),
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: Colors.grey.withOpacity(0.3 + value * 0.7),
                  shape: BoxShape.circle,
                ),
              );
            },
          );
        }),
      ),
    );
  }
}

class ImagePreviewSheet extends StatelessWidget {
  final String imagePath;
  final VoidCallback? onSend;
  final VoidCallback? onDelete;

  const ImagePreviewSheet({
    super.key,
    required this.imagePath,
    this.onSend,
    this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.8,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      child: Column(
        children: [
          // 顶部栏
          Container(
            padding: const EdgeInsets.all(8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.pop(context),
                ),
                const Text(
                  '预览',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                ),
                TextButton(
                  onPressed: onSend,
                  child: const Text('发送'),
                ),
              ],
            ),
          ),

          // 图片
          Expanded(
            child: Image.asset(
              imagePath,
              fit: BoxFit.contain,
              errorBuilder: (context, error, stackTrace) {
                return const Center(
                  child: Icon(Icons.broken_image, size: 64),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
