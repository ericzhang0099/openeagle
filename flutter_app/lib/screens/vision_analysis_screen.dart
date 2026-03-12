import 'package:flutter/material.dart';

class VisionAnalysisScreen extends StatefulWidget {
  const VisionAnalysisScreen({super.key});

  @override
  State<VisionAnalysisScreen> createState() => _VisionAnalysisScreenState();
}

class _VisionAnalysisScreenState extends State<VisionAnalysisScreen> {
  String? _selectedImage;
  String? _analysisResult;
  bool _isAnalyzing = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('视觉分析'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 选择图片
            const Text(
              '选择图片',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildImageSourceButton(
                    icon: Icons.camera_alt,
                    label: '拍照',
                    onTap: () {},
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildImageSourceButton(
                    icon: Icons.photo_library,
                    label: '相册',
                    onTap: () {},
                  ),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // 图片预览
            if (_selectedImage != null) ...[
              const Text(
                '预览',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              Container(
                height: 200,
                width: double.infinity,
                decoration: BoxDecoration(
                  color: Colors.grey[200],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Center(
                  child: Icon(Icons.image, size: 64, color: Colors.grey),
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isAnalyzing ? null : _analyzeImage,
                  child: _isAnalyzing
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('开始分析'),
                ),
              ),
            ],

            const SizedBox(height: 24),

            // 分析结果
            if (_analysisResult != null) ...[
              const Text(
                '分析结果',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(_analysisResult!),
                ),
              ),
            ],

            const SizedBox(height: 24),

            // 功能列表
            const Text(
              '分析功能',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            _buildFeatureCard(
              icon: Icons.search,
              title: '目标检测',
              description: '识别图片中的物体和位置',
            ),
            _buildFeatureCard(
              icon: Icons.text_fields,
              title: '文字识别',
              description: '提取图片中的文字内容',
            ),
            _buildFeatureCard(
              icon: Icons.face,
              title: '人脸识别',
              description: '检测人脸位置和特征',
            ),
            _buildFeatureCard(
              icon: Icons.image,
              title: '图像理解',
              description: '理解图片的整体内容和场景',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildImageSourceButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey[300]!),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          children: [
            Icon(icon, size: 32, color: Colors.blue),
            const SizedBox(height: 8),
            Text(label),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureCard({
    required IconData icon,
    required String title,
    required String description,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.blue[50],
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: Colors.blue),
        ),
        title: Text(title),
        subtitle: Text(description),
        trailing: const Icon(Icons.chevron_right),
        onTap: () {},
      ),
    );
  }

  Future<void> _analyzeImage() async {
    setState(() {
      _isAnalyzing = true;
    });

    // 模拟分析
    await Future.delayed(const Duration(seconds: 2));

    setState(() {
      _isAnalyzing = false;
      _analysisResult = '图片分析完成。这是一张包含多种物体的图片，主要识别到：\n\n1. 人物\n2. 背景\n3. 物品\n\n详细信息请查看完整报告。';
    });
  }
}
