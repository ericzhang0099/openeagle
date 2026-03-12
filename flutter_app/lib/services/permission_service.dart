import 'package:permission_handler/permission_handler.dart';

class PermissionService {
  // 检查权限
  Future<bool> checkCameraPermission() async {
    return await Permission.camera.isGranted;
  }

  Future<bool> checkMicrophonePermission() async {
    return await Permission.microphone.isGranted;
  }

  Future<bool> checkStoragePermission() async {
    return await Permission.storage.isGranted;
  }

  Future<bool> checkLocationPermission() async {
    return await Permission.location.isGranted;
  }

  // 请求权限
  Future<bool> requestCameraPermission() async {
    final status = await Permission.camera.request();
    return status.isGranted;
  }

  Future<bool> requestMicrophonePermission() async {
    final status = await Permission.microphone.request();
    return status.isGranted;
  }

  Future<bool> requestStoragePermission() async {
    final status = await Permission.storage.request();
    return status.isGranted;
  }

  Future<bool> requestLocationPermission() async {
    final status = await Permission.location.request();
    return status.isGranted;
  }

  // 检查并请求
  Future<bool> ensureCameraPermission() async {
    if (await checkCameraPermission()) return true;
    return await requestCameraPermission();
  }

  Future<bool> ensureMicrophonePermission() async {
    if (await checkMicrophonePermission()) return true;
    return await requestMicrophonePermission();
  }

  Future<bool> ensureStoragePermission() async {
    if (await checkStoragePermission()) return true;
    return await requestStoragePermission();
  }

  Future<bool> ensureLocationPermission() async {
    if (await checkLocationPermission()) return true;
    return await requestLocationPermission();
  }

  // 请求所有必要权限
  Future<Map<Permission, PermissionStatus>> requestAllPermissions() async {
    return await [
      Permission.camera,
      Permission.microphone,
      Permission.storage,
      Permission.location,
    ].request();
  }

  // 检查权限状态
  Future<PermissionStatus> getCameraStatus() async {
    return await Permission.camera.status;
  }

  Future<PermissionStatus> getMicrophoneStatus() async {
    return await Permission.microphone.status;
  }

  // 打开设置
  Future<bool> openSettings() async {
    return await openAppSettings();
  }

  // 是否被永久拒绝
  Future<bool> isCameraPermanentlyDenied() async {
    return await Permission.camera.isPermanentlyDenied;
  }

  Future<bool> isMicrophonePermanentlyDenied() async {
    return await Permission.microphone.isPermanentlyDenied;
  }
}
