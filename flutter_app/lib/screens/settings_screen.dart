import 'package:flutter/material.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  // 服务器配置
  final TextEditingController _serverUrlController = TextEditingController();
  final TextEditingController _wsUrlController = TextEditingController();

  // 功能开关
  bool _enableNotification = true;
  bool _enableVoice = true;
  bool _enableCamera = true;
  bool _autoConnect = true;
  bool _saveHistory = true;

  // 关于
  String _appVersion = '1.0.0';

  @override
  void dispose() {
    _serverUrlController.dispose();
    _wsUrlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('设置'),
      ),
      body: ListView(
        children: [
          // 服务器配置
          _buildSectionHeader('服务器配置'),
          ListTile(
            leading: const Icon(Icons.dns),
            title: const Text('服务器地址'),
            subtitle: Text(_serverUrlController.text.isEmpty
                ? '未设置'
                : _serverUrlController.text),
            onTap: () => _showServerUrlDialog(),
          ),
          ListTile(
            leading: const Icon(Icons.sync_alt),
            title: const Text('WebSocket地址'),
            subtitle: Text(_wsUrlController.text.isEmpty
                ? '未设置'
                : _wsUrlController.text),
            onTap: () => _showWsUrlDialog(),
          ),

          // 功能设置
          _buildSectionHeader('功能设置'),
          SwitchListTile(
            secondary: const Icon(Icons.notifications),
            title: const Text('消息通知'),
            subtitle: const Text('接收新消息通知'),
            value: _enableNotification,
            onChanged: (value) {
              setState(() => _enableNotification = value);
            },
          ),
          SwitchListTile(
            secondary: const Icon(Icons.mic),
            title: const Text('语音输入'),
            subtitle: const Text('启用语音识别'),
            value: _enableVoice,
            onChanged: (value) {
              setState(() => _enableVoice = value);
            },
          ),
          SwitchListTile(
            secondary: const Icon(Icons.camera_alt),
            title: const Text('摄像头'),
            subtitle: const Text('启用相机功能'),
            value: _enableCamera,
            onChanged: (value) {
              setState(() => _enableCamera = value);
            },
          ),
          SwitchListTile(
            secondary: const Icon(Icons.sync),
            title: const Text('自动连接'),
            subtitle: const Text('启动时自动连接服务器'),
            value: _autoConnect,
            onChanged: (value) {
              setState(() => _autoConnect = value);
            },
          ),
          SwitchListTile(
            secondary: const Icon(Icons.history),
            title: const Text('保存历史'),
            subtitle: const Text('保存聊天记录到本地'),
            value: _saveHistory,
            onChanged: (value) {
              setState(() => _saveHistory = value);
            },
          ),

          // 隐私设置
          _buildSectionHeader('隐私与安全'),
          ListTile(
            leading: const Icon(Icons.security),
            title: const Text('隐私政策'),
            onTap: () {
              // TODO: 打开隐私政策
            },
          ),
          ListTile(
            leading: const Icon(Icons.delete_forever),
            title: const Text('清除缓存'),
            onTap: () => _showClearCacheDialog(),
          ),
          ListTile(
            leading: const Icon(Icons.logout),
            title: const Text('退出登录'),
            onTap: () => _showLogoutDialog(),
          ),

          // 关于
          _buildSectionHeader('关于'),
          ListTile(
            leading: const Icon(Icons.info),
            title: const Text('版本信息'),
            subtitle: Text(_appVersion),
          ),
          ListTile(
            leading: const Icon(Icons.code),
            title: const Text('开源许可'),
            onTap: () {
              // TODO: 打开许可
            },
          ),
          ListTile(
            leading: const Icon(Icons.bug_report),
            title: const Text('问题反馈'),
            onTap: () {
              // TODO: 反馈问题
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
      child: Text(
        title,
        style: TextStyle(
          color: Theme.of(context).colorScheme.primary,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  void _showServerUrlDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('服务器地址'),
        content: TextField(
          controller: _serverUrlController,
          decoration: const InputDecoration(
            hintText: 'http://your-server:8000',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() {});
            },
            child: const Text('保存'),
          ),
        ],
      ),
    );
  }

  void _showWsUrlDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('WebSocket地址'),
        content: TextField(
          controller: _wsUrlController,
          decoration: const InputDecoration(
            hintText: 'ws://your-server:8000',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() {});
            },
            child: const Text('保存'),
          ),
        ],
      ),
    );
  }

  void _showClearCacheDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('清除缓存'),
        content: const Text('确定要清除所有缓存数据吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('缓存已清除')),
              );
            },
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }

  void _showLogoutDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('退出登录'),
        content: const Text('确定要退出登录吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: 执行退出登录
            },
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }
}
