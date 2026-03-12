import 'package:flutter/material.dart';
import '../services/audio_service.dart';

class VoiceRecordWidget extends StatefulWidget {
  final AudioService audioService;
  final Function(String) onRecordComplete;
  final VoidCallback? onCancel;

  const VoiceRecordWidget({
    super.key,
    required this.audioService,
    required this.onRecordComplete,
    this.onCancel,
  });

  @override
  State<VoiceRecordWidget> createState() => _VoiceRecordWidgetState();
}

class _VoiceRecordWidgetState extends State<VoiceRecordWidget>
    with SingleTickerProviderStateMixin {
  bool _isRecording = false;
  int _recordingSeconds = 0;
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat(reverse: true);

    _scaleAnimation = Tween<double>(begin: 1.0, end: 1.2).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _startRecording() async {
    final error = await widget.audioService.startRecording();
    if (error == null) {
      setState(() {
        _isRecording = true;
        _recordingSeconds = 0;
      });
      _startTimer();
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('录音失败: $error')),
        );
      }
    }
  }

  void _startTimer() {
    Future.doWhile(() async {
      await Future.delayed(const Duration(seconds: 1));
      if (!mounted || !_isRecording) return false;
      setState(() => _recordingSeconds++);
      return _isRecording;
    });
  }

  Future<void> _stopRecording() async {
    final filePath = await widget.audioService.stopRecording();
    setState(() => _isRecording = false);
    if (filePath != null) {
      widget.onRecordComplete(filePath);
    }
  }

  Future<void> _cancelRecording() async {
    await widget.audioService.cancelRecording();
    setState(() => _isRecording = false);
    widget.onCancel?.call();
  }

  String _formatTime(int seconds) {
    final minutes = seconds ~/ 60;
    final secs = seconds % 60;
    return '$minutes:${secs.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // 取消按钮
          if (_isRecording)
            IconButton(
              icon: const Icon(Icons.close, color: Colors.red),
              onPressed: _cancelRecording,
            ),

          // 录音按钮
          GestureDetector(
            onTap: _isRecording ? _stopRecording : _startRecording,
            child: AnimatedBuilder(
              animation: _scaleAnimation,
              builder: (context, child) {
                return Transform.scale(
                  scale: _isRecording ? _scaleAnimation.value : 1.0,
                  child: Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: _isRecording ? Colors.red : Colors.blue,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      _isRecording ? Icons.stop : Icons.mic,
                      color: Colors.white,
                      size: 24,
                    ),
                  ),
                );
              },
            ),
          ),

          // 录音时间
          if (_isRecording) ...[
            const SizedBox(width: 12),
            Text(
              _formatTime(_recordingSeconds),
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(width: 8),
            const Text(
              '松开结束',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey,
              ),
            ),
          ] else ...[
            const SizedBox(width: 12),
            const Text(
              '按住说话',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey,
              ),
            ),
          ],
        ],
      ),
    );
  }
}
