import 'dart:io';
import 'package:record/record.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:path/path.dart' as path;

class AudioService {
  final AudioRecorder _recorder = AudioRecorder();
  final AudioPlayer _player = AudioPlayer();

  bool _isRecording = false;
  String? _recordingPath;

  bool get isRecording => _isRecording;

  Future<bool> hasPermission() async {
    return await _recorder.hasPermission();
  }

  Future<String?> startRecording() async {
    if (_isRecording) return null;

    final hasPermission = await _recorder.hasPermission();
    if (!hasPermission) return '没有录音权限';

    final directory = Directory.systemTemp.path;
    final fileName = 'vision_claw_${DateTime.now().millisecondsSinceEpoch}.m4a';
    _recordingPath = path.join(directory, fileName);

    try {
      await _recorder.start(
        const RecordConfig(
          encoder: AudioEncoder.aacLc,
          sampleRate: 16000,
          numChannels: 1,
        ),
        path: _recordingPath!,
      );
      _isRecording = true;
      return null;
    } catch (e) {
      return e.toString();
    }
  }

  Future<String?> stopRecording() async {
    if (!_isRecording) return null;

    try {
      final filePath = await _recorder.stop();
      _isRecording = false;
      return filePath;
    } catch (e) {
      _isRecording = false;
      return null;
    }
  }

  Future<void> cancelRecording() async {
    if (!_isRecording) return;

    await _recorder.stop();
    _isRecording = false;

    // 删除临时文件
    if (_recordingPath != null) {
      final file = File(_recordingPath!);
      if (await file.exists()) {
        await file.delete();
      }
    }
    _recordingPath = null;
  }

  Future<void> playAudio(String filePath) async {
    await _player.play(DeviceFileSource(filePath));
  }

  Future<void> playAudioFromUrl(String url) async {
    await _player.play(UrlSource(url));
  }

  Future<void> stopPlayback() async {
    await _player.stop();
  }

  Future<void> pausePlayback() async {
    await _player.pause();
  }

  Future<void> resumePlayback() async {
    await _player.resume();
  }

  void dispose() {
    _recorder.dispose();
    _player.dispose();
  }
}
