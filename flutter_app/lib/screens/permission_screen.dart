import 'package:flutter/material.dart';
import '../services/permission_service.dart';

class PermissionScreen extends StatefulWidget {
  const PermissionScreen({super.key});

  @override
  State<PermissionScreen> createState() => _PermissionScreenState();
}

class _PermissionScreenState extends State<PermissionScreen> {
  final PermissionService _permissionService = PermissionService();

  bool _cameraGranted = false;
  bool _microphoneGranted = false;
  bool _storageGranted = false;
  bool _locationGranted = false;

  @override
  void initState() {
    super.initState();
    _checkPermissions();
  }

  Future<void> _checkPermissions() async {
    setState(() {
      _cameraGranted = await _permissionService.checkCameraPermission();
      _microphoneGranted = await _permissionService.checkMicrophonePermission();
      _storageGranted = await _permissionService.checkStoragePermission();
      _locationGranted = await _permissionService.checkLocationPermission();
    });
  }

  @override
  Widget build(BuildContext context) {
    final allGranted = _cameraGranted &&
        _microphoneGranted &&
        _storageGranted &&
        _locationGranted;

    return Scaffold(
      appBar: AppBar(
        title: const Text('权限申请'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '为了正常使用VisionClaw的所有功能，需要以下权限：',
              style: TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 24),

            // 相机权限
            _buildPermissionItem(
              icon: Icons.camera_alt,
              title: '相机',
              description: '用于拍照、录像和视频通话',
              granted: _cameraGranted,
              onRequest: () async {
                final granted = await _permissionService.ensureCameraPermission();
                setState(() => _cameraGranted = granted);
              },
            ),

            // 麦克风权限
            _buildPermissionItem(
              icon: Icons.mic,
              title: '麦克风',
              description: '用于语音输入和语音通话',
              granted: _microphoneGranted,
              onRequest: () async {
                final granted = await _permissionService.ensureMicrophonePermission();
                setState(() => _microphoneGranted = granted);
              },
            ),

            // 存储权限
            _buildPermissionItem(
              icon: Icons.folder,
              title: '存储',
              description: '用于保存照片、视频和文件',
              granted: _storageGranted,
              onRequest: () async {
                final granted = await _permissionService.ensureStoragePermission();
                setState(() => _storageGranted = granted);
              },
            ),

            // 位置权限
            _buildPermissionItem(
              icon: Icons.location_on,
              title: '位置',
              description: '用于定位和导航功能',
              granted: _locationGranted,
              onRequest: () async {
                final granted = await _permissionService.ensureLocationPermission();
                setState(() => _locationGranted = granted);
              },
            ),

            const Spacer(),

            // 状态提示
            if (!allGranted)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange[50],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info, color: Colors.orange[700]),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        '您可以选择拒绝部分权限，但相关功能将无法使用',
                        style: TextStyle(color: Colors.orange[700]),
                      ),
                    ),
                  ],
                ),
              ),

            const SizedBox(height: 16),

            // 按钮
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: allGranted
                    ? () {
                        // TODO: 跳转主页
                        Navigator.pop(context);
                      }
                    : () => _permissionService.openSettings(),
                child: Text(allGranted ? '完成' : '打开设置'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPermissionItem({
    required IconData icon,
    required String title,
    required String description,
    required bool granted,
    required VoidCallback onRequest,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: granted ? Colors.green[100] : Colors.grey[200],
            shape: BoxShape.circle,
          ),
          child: Icon(
            icon,
            color: granted ? Colors.green : Colors.grey,
          ),
        ),
        title: Text(title),
        subtitle: Text(description),
        trailing: granted
            ? const Icon(Icons.check_circle, color: Colors.green)
            : TextButton(
                onPressed: onRequest,
                child: const Text('授权'),
              ),
      ),
    );
  }
}
