import 'package:flutter/material.dart';

class Tool {
  final String name;
  final String description;
  final IconData icon;
  final VoidCallback onTap;

  const Tool({
    required this.name,
    required this.description,
    required this.icon,
    required this.onTap,
  });
}

class ToolsScreen extends StatelessWidget {
  const ToolsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final tools = [
      Tool(
        name: '语音识别',
        description: '将语音转换为文字',
        icon: Icons.mic,
        onTap: () {},
      ),
      Tool(
        name: '语音合成',
        description: '将文字转换为语音',
        icon: Icons.record_voice_over,
        onTap: () {},
      ),
      Tool(
        name: '图像识别',
        description: '分析图片内容',
        icon: Icons.image,
        onTap: () {},
      ),
      Tool(
        name: '文字识别',
        description: '提取图片中的文字',
        icon: Icons.text_fields,
        onTap: () {},
      ),
      Tool(
        name: '人脸识别',
        description: '检测和分析人脸',
        icon: Icons.face,
        onTap: () {},
      ),
      Tool(
        name: '目标检测',
        description: '识别物体位置',
        icon: Icons.center_focus_strong,
        onTap: () {},
      ),
      Tool(
        name: '位置服务',
        description: '获取当前位置',
        icon: Icons.location_on,
        onTap: () {},
      ),
      Tool(
        name: '传感器',
        description: '获取传感器数据',
        icon: Icons.sensors,
        onTap: () {},
      ),
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('工具箱'),
      ),
      body: GridView.builder(
        padding: const EdgeInsets.all(16),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 1.1,
        ),
        itemCount: tools.length,
        itemBuilder: (context, index) {
          final tool = tools[index];
          return _buildToolCard(tool);
        },
      ),
    );
  }

  Widget _buildToolCard(Tool tool) {
    return Card(
      child: InkWell(
        onTap: tool.onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(tool.icon, size: 28, color: Colors.blue),
              ),
              const SizedBox(height: 12),
              Text(
                tool.name,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                tool.description,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
