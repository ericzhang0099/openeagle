import 'package:flutter/material.dart';
import '../../models/message.dart';
import '../services/vision_claw_sdk.dart';
import '../services/audio_service.dart';
import '../services/image_picker_service.dart';
import '../widgets/message_bubble.dart';
import '../widgets/indicator_widgets.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _inputController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<Message> _messages = [];
  final AudioService _audioService = AudioService();
  final ImagePickerService _imagePickerService = ImagePickerService();
  
  bool _isLoading = false;
  bool _isRecording = false;
  int _recordingSeconds = 0;
  bool _isConnected = false;

  @override
  void initState() {
    super.initState();
    _initSDK();
  }

  Future<void> _initSDK() async {
    // 初始化SDK
    try {
      await VisionClawSDK.initialize();
      
      // 设置回调
      VisionClawSDK.instance.onMessageReceived = _onMessageReceived;
      VisionClawSDK.instance.onConnectionChanged = _onConnectionChanged;
      VisionClawSDK.instance.onError = _onError;
      
      // 连接服务器
      final connected = await VisionClawSDK.instance.connect();
      setState(() => _isConnected = connected);
    } catch (e) {
      debugPrint('SDK初始化失败: $e');
    }
  }

  void _onMessageReceived(Message message) {
    setState(() {
      _messages.add(message);
      _isLoading = false;
    });
    _scrollToBottom();
  }

  void _onConnectionChanged(bool connected) {
    setState(() => _isConnected = connected);
  }

  void _onError(String error) {
    setState(() => _isLoading = false);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('错误: $error')),
    );
  }

  @override
  void dispose() {
    _inputController.dispose();
    _scrollController.dispose();
    _audioService.dispose();
    VisionClawSDK.instance.dispose();
    super.dispose();
  }

  void _sendMessage() async {
    final text = _inputController.text.trim();
    if (text.isEmpty) return;

    // 添加用户消息
    final userMessage = Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      type: MessageType.text,
      content: text,
      timestamp: DateTime.now().millisecondsSinceEpoch,
      status: MessageStatus.sending,
      role: MessageRole.user,
    );

    setState(() {
      _messages.add(userMessage);
      _isLoading = true;
    });

    _inputController.clear();
    _scrollToBottom();

    try {
      // 发送消息
      final response = await VisionClawSDK.instance.sendText(text);
      
      if (response.isSuccess) {
        // 更新消息状态
        setState(() {
          final index = _messages.indexWhere((m) => m.id == userMessage.id);
          if (index != -1) {
            _messages[index] = userMessage.copyWith(status: MessageStatus.sent);
          }
        });
      } else {
        // 发送失败
        setState(() {
          final index = _messages.indexWhere((m) => m.id == userMessage.id);
          if (index != -1) {
            _messages[index] = userMessage.copyWith(status: MessageStatus.error);
          }
          _isLoading = false;
        });
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('发送失败: ${response.message}')),
          );
        }
      }
    } catch (e) {
      setState(() {
        final index = _messages.indexWhere((m) => m.id == userMessage.id);
        if (index != -1) {
          _messages[index] = userMessage.copyWith(status: MessageStatus.error);
        }
        _isLoading = false;
      });
    }
  }

  Future<void> _sendImage() async {
    try {
      final imagePath = await _imagePickerService.pickFromGallery();
      if (imagePath == null) return;

      // 添加用户消息
      final userMessage = Message(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: MessageType.image,
        content: imagePath,
        timestamp: DateTime.now().millisecondsSinceEpoch,
        status: MessageStatus.sending,
        role: MessageRole.user,
      );

      setState(() {
        _messages.add(userMessage);
      });
      _scrollToBottom();

      // 发送图片
      final response = await VisionClawSDK.instance.sendImage(imagePath);
      
      setState(() {
        final index = _messages.indexWhere((m) => m.id == userMessage.id);
        if (index != -1) {
          _messages[index] = userMessage.copyWith(
            status: response.isSuccess ? MessageStatus.sent : MessageStatus.error,
          );
        }
      });

      if (!response.isSuccess && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('发送失败: ${response.message}')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('发送图片失败: $e')),
        );
      }
    }
  }

  Future<void> _sendVoice() async {
    try {
      final audioPath = await _audioService.startRecording();
      if (audioPath == null) return;

      // 添加用户消息
      final userMessage = Message(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: MessageType.voice,
        content: audioPath,
        timestamp: DateTime.now().millisecondsSinceEpoch,
        status: MessageStatus.sending,
        role: MessageRole.user,
      );

      setState(() {
        _messages.add(userMessage);
        _isRecording = true;
        _recordingSeconds = 0;
      });
      _scrollToBottom();

      // 开始录音计时
      _startRecordingTimer();

      // 停止录音
      final stopResult = await _audioService.stopRecording();
      
      setState(() {
        _isRecording = false;
      });

      if (stopResult == null) {
        // 录音失败
        setState(() {
          final index = _messages.indexWhere((m) => m.id == userMessage.id);
          if (index != -1) {
            _messages[index] = userMessage.copyWith(status: MessageStatus.error);
          }
        });
        return;
      }

      // 发送语音
      final response = await VisionClawSDK.instance.sendVoice(stopResult);
      
      setState(() {
        final index = _messages.indexWhere((m) => m.id == userMessage.id);
        if (index != -1) {
          _messages[index] = userMessage.copyWith(
            status: response.isSuccess ? MessageStatus.sent : MessageStatus.error,
          );
        }
      });
    } catch (e) {
      setState(() => _isRecording = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('发送语音失败: $e')),
        );
      }
    }
  }

  void _startRecordingTimer() {
    Future.doWhile(() async {
      await Future.delayed(const Duration(seconds: 1));
      if (!mounted || !_isRecording) return false;
      setState(() => _recordingSeconds++);
      return _isRecording;
    });
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('VisionClaw'),
        actions: [
          // 连接状态
          Container(
            margin: const EdgeInsets.only(right: 8),
            child: Row(
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: _isConnected ? Colors.green : Colors.red,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 4),
                Text(
                  _isConnected ? '已连接' : '未连接',
                  style: const TextStyle(fontSize: 12),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.camera_alt),
            onPressed: () async {
              final imagePath = await _imagePickerService.pickFromCamera();
              if (imagePath != null) {
                // 发送图片
                final userMessage = Message(
                  id: DateTime.now().millisecondsSinceEpoch.toString(),
                  type: MessageType.image,
                  content: imagePath,
                  timestamp: DateTime.now().millisecondsSinceEpoch,
                  status: MessageStatus.sent,
                  role: MessageRole.user,
                );
                setState(() => _messages.add(userMessage));
              }
            },
          ),
          IconButton(
            icon: const Icon(Icons.image),
            onPressed: _sendImage,
          ),
        ],
      ),
      body: Column(
        children: [
          // 消息列表
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length + (_isLoading ? 1 : 0),
              itemBuilder: (context, index) {
                if (index == _messages.length && _isLoading) {
                  return const TypingIndicator();
                }
                return MessageBubble(
                  message: _messages[index],
                  onTap: () {
                    // 消息点击处理
                  },
                );
              },
            ),
          ),
          
          // 输入区域
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildInputArea() {
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
        child: Row(
          children: [
            // 更多按钮
            IconButton(
              icon: const Icon(Icons.add_circle_outline),
              onPressed: () {
                _showMoreOptions();
              },
            ),

            // 文本输入
            Expanded(
              child: TextField(
                controller: _inputController,
                decoration: InputDecoration(
                  hintText: _isRecording ? '录音中...' : '发送消息...',
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
                enabled: !_isRecording,
                textInputAction: TextInputAction.send,
                onSubmitted: (_) => _sendMessage(),
              ),
            ),

            const SizedBox(width: 8),

            // 发送/录音按钮
            if (_isRecording)
              _buildRecordingButton()
            else
              _buildSendButton(),
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
        onPressed: _sendMessage,
      ),
    );
  }

  Widget _buildRecordingButton() {
    return GestureDetector(
      onTap: _sendVoice,
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
              '${_recordingSeconds}s',
              style: const TextStyle(color: Colors.white),
            ),
          ],
        ),
      ),
    );
  }

  void _showMoreOptions() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt),
              title: const Text('拍照'),
              onTap: () {
                Navigator.pop(context);
                // TODO: 打开相机
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text('从相册选择'),
              onTap: () {
                Navigator.pop(context);
                _sendImage();
              },
            ),
            ListTile(
              leading: const Icon(Icons.location_on),
              title: const Text('发送位置'),
              onTap: () {
                Navigator.pop(context);
                // TODO: 发送位置
              },
            ),
            ListTile(
              leading: const Icon(Icons.file_present),
              title: const Text('发送文件'),
              onTap: () {
                Navigator.pop(context);
                // TODO: 发送文件
              },
            ),
          ],
        ),
      ),
    );
  }
}
