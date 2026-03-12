import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import '../services/camera_service.dart';
import '../services/image_picker_service.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> with WidgetsBindingObserver {
  final CameraService _cameraService = CameraService();
  final ImagePickerService _imagePickerService = ImagePickerService();
  
  bool _isInitialized = false;
  bool _isRecording = false;
  String? _errorMessage;
  
  // 相机设置
  FlashMode _flashMode = FlashMode.off;
  int _currentCameraIndex = 0;
  double _zoomLevel = 1.0;
  double _minZoom = 1.0;
  double _maxZoom = 1.0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initCamera();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _cameraService.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (!_isInitialized) return;

    if (state == AppLifecycleState.inactive) {
      _cameraService.dispose();
    } else if (state == AppLifecycleState.resumed) {
      _initCamera();
    }
  }

  Future<void> _initCamera() async {
    try {
      await _cameraService.startCamera(cameraIndex: _currentCameraIndex);
      
      // 获取缩放范围
      _minZoom = await _cameraService.controller!.getMinZoomLevel();
      _maxZoom = await _cameraService.controller!.getMaxZoomLevel();
      
      setState(() {
        _isInitialized = true;
        _errorMessage = null;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
      });
    }
  }

  Future<void> _takePicture() async {
    if (!_isInitialized) return;

    try {
      final file = await _cameraService.takePicture();
      if (file != null && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('照片已保存: ${file.path}'),
            action: SnackBarAction(
              label: '查看',
              onPressed: () {
                // TODO: 打开图片查看
              },
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('拍照失败: $e')),
        );
      }
    }
  }

  Future<void> _startVideoRecording() async {
    if (!_isInitialized || _isRecording) return;

    try {
      final error = await _cameraService.startVideoRecording();
      if (error == null) {
        setState(() => _isRecording = true);
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('录像失败: $error')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('录像失败: $e')),
        );
      }
    }
  }

  Future<void> _stopVideoRecording() async {
    if (!_isRecording) return;

    try {
      final file = await _cameraService.stopVideoRecording();
      setState(() => _isRecording = false);
      
      if (file != null && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('录像已保存: ${file.path}')),
        );
      }
    } catch (e) {
      setState(() => _isRecording = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('停止录像失败: $e')),
        );
      }
    }
  }

  Future<void> _switchCamera() async {
    if (_isRecording) return;
    
    setState(() {
      _currentCameraIndex = (_currentCameraIndex + 1) % 2;
    });
    await _initCamera();
  }

  Future<void> _toggleFlash() async {
    if (!_isInitialized) return;

    final modes = [FlashMode.off, FlashMode.auto, FlashMode.always];
    final currentIndex = modes.indexOf(_flashMode);
    final nextIndex = (currentIndex + 1) % modes.length;
    
    await _cameraService.setFlashMode(modes[nextIndex]);
    setState(() => _flashMode = modes[nextIndex]);
  }

  Future<void> _setZoom(double zoom) async {
    if (!_isInitialized) return;
    
    final clampedZoom = zoom.clamp(_minZoom, _maxZoom);
    await _cameraService.setZoom(clampedZoom);
    setState(() => _zoomLevel = clampedZoom);
  }

  Future<void> _pickFromGallery() async {
    final imagePath = await _imagePickerService.pickFromCamera();
    if (imagePath != null && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('已选择图片: $imagePath')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_errorMessage != null) {
      return Scaffold(
        appBar: AppBar(title: const Text('相机')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              Text('相机初始化失败:\n$_errorMessage'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _initCamera,
                child: const Text('重试'),
              ),
            ],
          ),
        ),
      );
    }

    if (!_isInitialized) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    return Scaffold(
      body: Stack(
        children: [
          // 相机预览
          Positioned.fill(
            child: CameraPreview(_cameraService.controller!),
          ),
          
          // 顶部控制栏
          SafeArea(
            child: Column(
              children: [
                // 顶部按钮
                Padding(
                  padding: const EdgeInsets.all(8),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      // 关闭按钮
                      IconButton(
                        icon: const Icon(Icons.close, color: Colors.white, size: 28),
                        onPressed: () => Navigator.pop(context),
                      ),
                      
                      // 闪光灯
                      IconButton(
                        icon: Icon(
                          _flashMode == FlashMode.off
                              ? Icons.flash_off
                              : _flashMode == FlashMode.auto
                                  ? Icons.flash_auto
                                  : Icons.flash_on,
                          color: Colors.white,
                          size: 28,
                        ),
                        onPressed: _toggleFlash,
                      ),
                    ],
                  ),
                ),
                
                // 缩放控制
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Row(
                    children: [
                      const Icon(Icons.zoom_out, color: Colors.white),
                      Expanded(
                        child: Slider(
                          value: _zoomLevel,
                          min: _minZoom,
                          max: _maxZoom,
                          onChanged: _setZoom,
                        ),
                      ),
                      const Icon(Icons.zoom_in, color: Colors.white),
                    ],
                  ),
                ),
              ],
            ),
          ),
          
          // 底部控制栏
          Positioned(
            bottom: 40,
            left: 0,
            right: 0,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                // 相册按钮
                IconButton(
                  icon: const Icon(Icons.photo_library, color: Colors.white, size: 32),
                  onPressed: _pickFromGallery,
                ),
                
                // 拍照/录像按钮
                GestureDetector(
                  onTap: _isRecording ? _stopVideoRecording : _takePicture,
                  onLongPress: _startVideoRecording,
                  child: Container(
                    width: 70,
                    height: 70,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.white, width: 4),
                    ),
                    child: Container(
                      margin: const EdgeInsets.all(4),
                      decoration: BoxDecoration(
                        shape: _isRecording ? BoxShape.rectangle : BoxShape.circle,
                        borderRadius: _isRecording ? BorderRadius.circular(8) : null,
                        color: _isRecording ? Colors.red : Colors.white,
                      ),
                    ),
                  ),
                ),
                
                // 切换摄像头
                IconButton(
                  icon: const Icon(Icons.flip_camera_ios, color: Colors.white, size: 32),
                  onPressed: _isRecording ? null : _switchCamera,
                ),
              ],
            ),
          ),
          
          // 录像标识
          if (_isRecording)
            Positioned(
              top: 80,
              left: 0,
              right: 0,
              child: Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.red,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.fiber_manual_record, color: Colors.white, size: 16),
                      SizedBox(width: 8),
                      Text('录像中', style: TextStyle(color: Colors.white)),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
