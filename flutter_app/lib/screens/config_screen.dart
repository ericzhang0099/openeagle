import 'package:flutter/material.dart';
import '../services/vision_claw_sdk.dart';
import '../models/app_config.dart';
import '../services/storage_service.dart';
import '../constants/constants.dart';

class ConfigScreen extends StatefulWidget {
  const ConfigScreen({super.key});

  @override
  State<ConfigScreen> createState() => _ConfigScreenState();
}

class _ConfigScreenState extends State<ConfigScreen> {
  final _serverUrlController = TextEditingController();
  final _wsUrlController = TextEditingController();
  final _apiKeyController = TextEditingController();
  
  bool _isLoading = false;
  bool _autoConnect = true;
  bool _enableNotification = true;
  bool _saveHistory = true;
  bool _darkMode = false;

  @override
  void initState() {
    super.initState();
    _loadConfig();
  }

  Future<void> _loadConfig() async {
    final storage = StorageService();
    await storage.init();
    
    setState(() {
      _serverUrlController.text = storage.getString(AppConstants.keyServerUrl) ?? '';
      _autoConnect = storage.getBool('auto_connect') ?? true;
      _enableNotification = storage.getBool('enable_notification') ?? true;
      _saveHistory = storage.getBool('save_history') ?? true;
      _darkMode = storage.getBool('dark_mode') ?? false;
    });
  }

  Future<void> _saveConfig() async {
    setState(() => _isLoading = true);
    
    try {
      final storage = StorageService();
      await storage.init();
      
      await storage.setString(AppConstants.keyServerUrl, _serverUrlController.text);
      await storage.setBool('auto_connect', _autoConnect);
      await storage.setBool('enable_notification', _enableNotification);
      await storage.setBool('save_history', _saveHistory);
      await storage.setBool('dark_mode', _darkMode);
      
      // 更新SDK配置
      final newConfig = AppConfig(
        baseUrl: _serverUrlController.text,
        wsUrl: _wsUrlController.text.isNotEmpty 
            ? _wsUrlController.text 
            : _serverUrlController.text.replaceAll('http', 'ws'),
      );
      await VisionClawSDK.initialize(config: newConfig);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('配置已保存')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('保存失败: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _testConnection() async {
    setState(() => _isLoading = true);
    
    try {
      // 尝试连接
      await VisionClawSDK.initialize(config: AppConfig(
        baseUrl: _serverUrlController.text,
        wsUrl: _wsUrlController.text.isNotEmpty 
            ? _wsUrlController.text 
            : _serverUrlController.text.replaceAll('http', 'ws'),
      ));
      
      final connected = await VisionClawSDK.instance.connect();
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(connected ? '连接成功' : '连接失败'),
            backgroundColor: connected ? Colors.green : Colors.red,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('连接失败: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _serverUrlController.dispose();
    _wsUrlController.dispose();
    _apiKeyController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('服务器配置'),
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
            onTap: () => _showUrlDialog('服务器地址', _serverUrlController),
          ),
          ListTile(
            leading: const Icon(Icons.sync_alt),
            title: const Text('WebSocket地址'),
            subtitle: Text(_wsUrlController.text.isEmpty 
                ? '自动' 
                : _wsUrlController.text),
            onTap: () => _showUrlDialog('WebSocket地址', _wsUrlController),
          ),
          ListTile(
            leading: const Icon(Icons.key),
            title: const Text('API密钥'),
            subtitle: const Text('点击设置'),
            onTap: () => _showUrlDialog('API密钥', _apiKeyController, obscure: true),
          ),
          
          // 连接按钮
          Padding(
            padding: const EdgeInsets.all(16),
            child: ElevatedButton(
              onPressed: _isLoading ? null : _testConnection,
              child: _isLoading 
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('测试连接'),
            ),
          ),

          const Divider(),

          // 功能设置
          _buildSectionHeader('功能设置'),
          SwitchListTile(
            secondary: const Icon(Icons.sync),
            title: const Text('自动连接'),
            subtitle: const Text('启动时自动连接服务器'),
            value: _autoConnect,
            onChanged: (value) => setState(() => _autoConnect = value),
          ),
          SwitchListTile(
            secondary: const Icon(Icons.notifications),
            title: const Text('消息通知'),
            subtitle: const Text('接收新消息通知'),
            value: _enableNotification,
            onChanged: (value) => setState(() => _enableNotification = value),
          ),
          SwitchListTile(
            secondary: const Icon(Icons.history),
            title: const Text('保存历史'),
            subtitle: const Text('保存聊天记录到本地'),
            value: _saveHistory,
            onChanged: (value) => setState(() => _saveHistory = value),
          ),
          SwitchListTile(
            secondary: const Icon(Icons.dark_mode),
            title: const Text('深色模式'),
            subtitle: const Text('使用深色主题'),
            value: _darkMode,
            onChanged: (value) => setState(() => _darkMode = value),
          ),

          const Divider(),

          // 存储管理
          _buildSectionHeader('存储管理'),
          ListTile(
            leading: const Icon(Icons.folder),
            title: const Text('清除缓存'),
            subtitle: const Text('释放存储空间'),
            onTap: () => _showClearCacheDialog(),
          ),
          ListTile(
            leading: const Icon(Icons.delete_forever),
            title: const Text('清除历史'),
            subtitle: const Text('删除所有聊天记录'),
            onTap: () => _showClearHistoryDialog(),
          ),

          const Divider(),

          // 保存按钮
          Padding(
            padding: const EdgeInsets.all(16),
            child: ElevatedButton(
              onPressed: _isLoading ? null : _saveConfig,
              child: const Text('保存配置'),
            ),
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

  void _showUrlDialog(String title, TextEditingController controller, {bool obscure = false}) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: TextField(
          controller: controller,
          obscureText: obscure,
          decoration: InputDecoration(
            hintText: obscure ? '请输入$title' : 'http://your-server:8000',
          ),
          onChanged: (_) => setState(() {}),
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
            onPressed: () async {
              Navigator.pop(context);
              // TODO: 清除缓存
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

  void _showClearHistoryDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('清除历史'),
        content: const Text('确定要删除所有聊天记录吗？此操作不可恢复。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.pop(context);
              // TODO: 清除历史
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('历史记录已清除')),
              );
            },
            child: const Text('确定', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
}
