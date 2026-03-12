import 'package:flutter/material.dart';
import '../models/message.dart';

class ChatInputBar extends StatefulWidget {
  final Function(String) onSendText;
  final Function(String) onSendImage;
  final Function(String) onSendVoice;
  final VoidCallback onStartRecording;
  final VoidCallback onStopRecording;
  final bool isRecording;
  final int recordingSeconds;

  const ChatInputBar({
    super.key,
    required this.onSendText,
    required this.onSendImage,
    required this.onSendVoice,
    required this.onStartRecording,
    required this.onStopRecording,
    required this.isRecording,
    required this.recordingSeconds,
  });

  @override
  State<ChatInputBar> createState() => _ChatInputBarState();
}

class _ChatInputBarState extends State<ChatInputBar> {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();
  bool _showActions = false;

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _sendText() {
    final text = _controller.text.trim();
    if (text.isNotEmpty) {
      widget.onSendText(text);
      _controller.clear();
    }
  }

  String _formatTime(int seconds) {
    final minutes = seconds ~/ 60;
    final secs = seconds % 60;
    return '$minutes:${secs.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // 操作按钮行
            if (_showActions)
              Container(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildActionButton(
                      icon: Icons.camera_alt,
                      label: '拍照',
                      onTap: () {
                        setState(() => _showActions = false);
                        // TODO: 打开相机
                      },
                    ),
                    _buildActionButton(
                      icon: Icons.photo_library,
                      label: '相册',
                      onTap: () {
                        setState(() => _showActions = false);
                        widget.onSendImage('');
                      },
                    ),
                    _buildActionButton(
                      icon: Icons.location_on,
                      label: '位置',
                      onTap: () {
                        setState(() => _showActions = false);
                      },
                    ),
                    _buildActionButton(
                      icon: Icons.file_present,
                      label: '文件',
                      onTap: () {
                        setState(() => _showActions = false);
                      },
                    ),
                  ],
                ),
              ),

            // 输入行
            Row(
              children: [
                // 更多按钮
                IconButton(
                  icon: Icon(
                    _showActions ? Icons.close : Icons.add_circle_outline,
                  ),
                  onPressed: () {
                    setState(() => _showActions = !_showActions);
                  },
                ),

                // 文本输入
                Expanded(
                  child: Container(
                    constraints: const BoxConstraints(maxHeight: 120),
                    child: TextField(
                      controller: _controller,
                      focusNode: _focusNode,
                      decoration: InputDecoration(
                        hintText: '发送消息...',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: BorderSide.none,
                        ),
                        filled: true,
                        fillColor: Colors.grey[100],
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 8,
                        ),
                      ),
                      maxLines: null,
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _sendText(),
                    ),
                  ),
                ),

                const SizedBox(width: 8),

                // 发送/录音按钮
                if (widget.isRecording)
                  _buildRecordingButton()
                else
                  _buildSendButton(),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSendButton() {
    return Container(
      decoration: const BoxDecoration(
        color: Colors.blue,
        shape: BoxShape.circle,
      ),
      child: IconButton(
        icon: const Icon(Icons.send, color: Colors.white),
        onPressed: _sendText,
      ),
    );
  }

  Widget _buildRecordingButton() {
    return GestureDetector(
      onTap: widget.onStopRecording,
      onLongPressEnd: (_) => widget.onStopRecording(),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: Colors.red,
          borderRadius: BorderRadius.circular(24),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.mic, color: Colors.white, size: 20),
            const SizedBox(width: 4),
            Text(
              _formatTime(widget.recordingSeconds),
              style: const TextStyle(color: Colors.white),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: Colors.blue),
            const SizedBox(height: 4),
            Text(label, style: const TextStyle(fontSize: 12)),
          ],
        ),
      ),
    );
  }
}
