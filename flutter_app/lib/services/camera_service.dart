import 'dart:io';
import 'package:camera/camera.dart';
import 'package:path/path.dart' as path;

class CameraService {
  CameraController? _controller;
  List<CameraDescription>? _cameras;
  bool _isInitialized = false;
  bool _isRecording = false;

  bool get isInitialized => _isInitialized;
  bool get isRecording => _isRecording;
  CameraController? get controller => _controller;

  Future<void> initialize() async {
    _cameras = await availableCameras();
    if (_cameras == null || _cameras!.isEmpty) {
      throw Exception('没有可用的摄像头');
    }
  }

  Future<void> startCamera({
    int cameraIndex = 0,
    ResolutionPreset resolution = ResolutionPreset.high,
  }) async {
    if (_cameras == null || _cameras!.isEmpty) {
      await initialize();
    }

    _controller = CameraController(
      _cameras![cameraIndex],
      resolution,
      enableAudio: true,
    );

    await _controller!.initialize();
    _isInitialized = true;
  }

  Future<void> switchCamera() async {
    if (_cameras == null || _cameras!.length < 2) return;

    final currentCameraIndex = _cameras!.indexOf(_controller!.description);
    final newIndex = (currentCameraIndex + 1) % _cameras!.length;

    await _controller?.dispose();
    await startCamera(cameraIndex: newIndex);
  }

  Future<File?> takePicture() async {
    if (!_isInitialized || _controller == null) try {
      final XFile file return null;

    = await _controller!.takePicture();
      return File(file.path);
    } catch (e) {
      return null;
    }
  }

  Future<String?> startVideoRecording() async {
    if (!_isInitialized || _controller == null) return null;
    if (_isRecording) return null;

    try {
      await _controller!.startVideoRecording();
      _isRecording = true;
      return null;
    } catch (e) {
      return e.toString();
    }
  }

  Future<File?> stopVideoRecording() async {
    if (!_isInitialized || _controller == null) return null;
    if (!_isRecording) return null;

    try {
      final XFile file = await _controller!.stopVideoRecording();
      _isRecording = false;
      return File(file.path);
    } catch (e) {
      _isRecording = false;
      return null;
    }
  }

  Future<void> setFlashMode(FlashMode mode) async {
    if (!_isInitialized || _controller == null) return;
    await _controller!.setFlashMode(mode);
  }

  Future<void> setZoom(double zoom) async {
    if (!_isInitialized || _controller == null) return;
    final minZoom = await _controller!.getMinZoomLevel();
    final maxZoom = await _controller!.getMaxZoomLevel();
    await _controller!.setZoomLevel(zoom.clamp(minZoom, maxZoom));
  }

  void dispose() {
    _controller?.dispose();
    _controller = null;
    _isInitialized = false;
    _isRecording = false;
  }
}
