import 'package:flutter/material.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('个人资料'),
      ),
      body: ListView(
        children: [
          // 头像
          Container(
            padding: const EdgeInsets.all(32),
            child: Column(
              children: [
                Stack(
                  children: [
                    CircleAvatar(
                      radius: 50,
                      backgroundColor: Colors.blue,
                      child: const Icon(
                        Icons.person,
                        size: 50,
                        color: Colors.white,
                      ),
                    ),
                    Positioned(
                      bottom: 0,
                      right: 0,
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        decoration: const BoxDecoration(
                          color: Colors.blue,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.camera_alt,
                          size: 16,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                const Text(
                  '用户',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),

          // 信息项
          _buildInfoItem(
            icon: Icons.person_outline,
            title: '昵称',
            value: '用户',
            onTap: () {},
          ),
          _buildInfoItem(
            icon: Icons.phone_outlined,
            title: '手机号',
            value: '未绑定',
            onTap: () {},
          ),
          _buildInfoItem(
            icon: Icons.email_outlined,
            title: '邮箱',
            value: '未绑定',
            onTap: () {},
          ),
          _buildInfoItem(
            icon: Icons.qr_code,
            title: '二维码名片',
            onTap: () {},
          ),

          const Divider(height: 32),

          _buildInfoItem(
            icon: Icons.lock_outline,
            title: '修改密码',
            onTap: () {},
          ),
          _buildInfoItem(
            icon: Icons.security,
            title: '安全中心',
            onTap: () {},
          ),
        ],
      ),
    );
  }

  Widget _buildInfoItem({
    required IconData icon,
    required String title,
    String? value,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (value != null)
            Text(
              value,
              style: TextStyle(color: Colors.grey[600]),
            ),
          const SizedBox(width: 8),
          const Icon(Icons.chevron_right),
        ],
      ),
      onTap: onTap,
    );
  }
}

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('关于'),
      ),
      body: ListView(
        children: [
          // Logo
          Container(
            padding: const EdgeInsets.all(32),
            child: Column(
              children: [
                Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: Colors.blue,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: const Icon(
                    Icons.visibility,
                    size: 40,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 16),
                const Text(
                  'VisionClaw',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '版本 1.0.0',
                  style: TextStyle(color: Colors.grey[600]),
                ),
              ],
            ),
          ),

          const Divider(),

          // 介绍
          ListTile(
            leading: const Icon(Icons.info_outline),
            title: const Text('应用介绍'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.description_outlined),
            title: const Text('用户协议'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.privacy_tip_outlined),
            title: const Text('隐私政策'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.article_outlined),
            title: const Text('开源许可'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {},
          ),

          const Divider(),

          // 联系方式
          ListTile(
            leading: const Icon(Icons.feedback_outlined),
            title: const Text('意见反馈'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.help_outline),
            title: const Text('帮助中心'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.update),
            title: const Text('检查更新'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {},
          ),

          const SizedBox(height: 32),

          // 版权
          Center(
            child: Text(
              '© 2026 VisionClaw',
              style: TextStyle(color: Colors.grey[400]),
            ),
          ),

          const SizedBox(height: 32),
        ],
      ),
    );
  }
}
