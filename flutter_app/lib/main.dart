import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/vision_claw_sdk.dart';
import '../services/storage_service.dart';
import '../screens/chat_screen.dart';
import '../screens/settings_screen.dart';
import '../screens/camera_screen.dart';
import '../screens/permission_screen.dart';
import '../screens/config_screen.dart';
import '../utils/state_manager.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // 初始化存储
  final storage = StorageService();
  await storage.init();
  
  runApp(const VisionClawApp());
}

class VisionClawApp extends StatelessWidget {
  const VisionClawApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<AppStateManager>(create: (_) => AppStateManager()),
        Provider<SessionManager>(create: (_) => SessionManager()),
        Provider<UserManager>(create: (_) => UserManager()),
      ],
      child: Consumer<AppStateManager>(
        builder: (context, appState, _) {
          return MaterialApp(
            title: 'VisionClaw',
            debugShowCheckedModeBanner: false,
            theme: ThemeManager.lightTheme,
            darkTheme: ThemeManager.darkTheme,
            themeMode: appState.isDarkMode ? ThemeMode.dark : ThemeMode.light,
            home: const SplashScreen(),
          );
        },
      ),
    );
  }
}

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _initialize();
  }

  Future<void> _initialize() async {
    await Future.delayed(const Duration(seconds: 2));
    
    if (!mounted) return;
    
    final storage = StorageService();
    final isFirstLaunch = storage.getBool('is_first_launch') ?? true;
    
    if (isFirstLaunch) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const PermissionScreen()),
      );
      await storage.setBool('is_first_launch', false);
    } else {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const HomeScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primary,
                borderRadius: BorderRadius.circular(24),
              ),
              child: const Icon(
                Icons.visibility,
                size: 64,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'VisionClaw',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '视觉智能体',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 48),
            const CircularProgressIndicator(),
          ],
        ),
      ),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;
  bool _isConnected = false;

  final List<Widget> _pages = [
    const ChatScreen(),
    const CameraScreen(),
    const ConfigScreen(),
  ];

  @override
  void initState() {
    super.initState();
    _connectToServer();
  }

  Future<void> _connectToServer() async {
    try {
      // 尝试连接
      final connected = await VisionClawSDK.instance.connect();
      if (mounted) {
        setState(() => _isConnected = connected);
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isConnected = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _pages,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) {
          setState(() => _currentIndex = index);
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.chat_outlined),
            selectedIcon: Icon(Icons.chat),
            label: '对话',
          ),
          NavigationDestination(
            icon: Icon(Icons.camera_alt_outlined),
            selectedIcon: Icon(Icons.camera_alt),
            label: '相机',
          ),
          NavigationDestination(
            icon: Icon(Icons.settings_outlined),
            selectedIcon: Icon(Icons.settings),
            label: '设置',
          ),
        ],
      ),
    );
  }
}
