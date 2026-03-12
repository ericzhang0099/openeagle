# Agent通信协议技术设计方案 (TDD)

**版本**: v1.0
**日期**: 2026-02-28
**状态**: 初稿

---

## 一、技术架构

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端层                                  │
│    (Agent SDK - Python / JavaScript / Go)                      │
├─────────────────────────────────────────────────────────────────┤
│                         接入层                                    │
│    (WebSocket Server / API Gateway)                            │
├─────────────────────────────────────────────────────────────────┤
│                         路由层                                    │
│    (Message Router / Load Balancer)                            │
├─────────────────────────────────────────────────────────────────┤
│                         服务层                                    │
│    (Auth / Message / Presence / Discovery)                     │
├─────────────────────────────────────────────────────────────────┤
│                         存储层                                    │
│    (Redis / SQLite / File Storage)                             │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 技术栈

| 层级 | 技术选型 | 理由 |
|------|----------|------|
| **语言** | Python 3.11+ | AI生态丰富 |
| **Web框架** | FastAPI | 高性能 + 自动API |
| **WebSocket** | websockets | 异步支持 |
| **数据库** | SQLite | MVP轻量 |
| **缓存** | Redis | 状态缓存 |
| **消息队列** | asyncio.Queue | 内存队列 |

---

## 二、模块设计

### 2.1 核心模块

```
┌─────────────────────────────────────────────────────────────────┐
│                        Core Modules                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Gateway   │  │   Message   │  │  Presence   │            │
│  │   网关      │  │   消息      │  │   状态      │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Discovery   │  │    Auth    │  │  Session    │            │
│  │   发现      │  │   认证      │  │   会话      │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 模块详细设计

#### 2.2.1 网关模块 (Gateway)

```python
class Gateway:
    """WebSocket网关"""
    
    async def handle_connect(self, websocket: WebSocket):
        """处理连接"""
        # 1. 接受连接
        await websocket.accept()
        
        # 2. 身份验证
        auth_result = await self.authenticate(websocket)
        if not auth_result.success:
            await websocket.close(1008, "Authentication failed")
            return
            
        # 3. 注册到连接管理器
        self.connection_manager.add(
            agent_id=auth_result.agent_id,
            websocket=websocket
        )
        
        # 4. 启动消息处理
        await self.handle_messages(websocket, auth_result.agent_id)
```

#### 2.2.2 消息模块 (Message)

```python
class MessageService:
    """消息服务"""
    
    async def send_message(self, message: Message) -> SendResult:
        """发送消息"""
        # 1. 验证消息格式
        await self.validate(message)
        
        # 2. 存储消息
        await self.storage.save(message)
        
        # 3. 投递消息
        if await self.presence.is_online(message.recipient):
            await self.deliver_online(message)
        else:
            await self.store_offline(message)
            
        # 4. 返回结果
        return SendResult(success=True, message_id=message.id)
```

#### 2.2.3 状态模块 (Presence)

```python
class PresenceService:
    """在线状态服务"""
    
    async def set_online(self, agent_id: str):
        """设置在线"""
        await self.redis.setex(
            f"presence:{agent_id}",
            30,  # 30秒超时
            "online"
        )
        
    async def is_online(self, agent_id: str) -> bool:
        """检查在线"""
        return await self.redis.exists(f"presence:{agent_id}")
        
    async def handle_heartbeat(self, agent_id: str):
        """处理心跳"""
        await self.set_online(agent_id)
```

#### 2.2.4 发现模块 (Discovery)

```python
class DiscoveryService:
    """发现服务"""
    
    async def register(self, agent: AgentInfo) -> AgentCard:
        """注册Agent"""
        # 1. 验证DID
        await self.auth.verify_did(agent.did)
        
        # 2. 创建Agent Card
        card = AgentCard(
            did=agent.did,
            name=agent.name,
            capabilities=agent.capabilities,
            endpoints=agent.endpoints
        )
        
        # 3. 存储
        await self.storage.save_card(card)
        
        return card
        
    async def search(self, query: SearchQuery) -> List[AgentCard]:
        """搜索Agent"""
        return await self.storage.search_agents(query)
```

---

## 三、数据库设计

### 3.1 表结构

```sql
-- Agent表
CREATE TABLE agents (
    did VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128),
    description TEXT,
    public_key TEXT,
    created_at BIGINT,
    updated_at BIGINT
);

-- 消息表
CREATE TABLE messages (
    id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64),
    sender VARCHAR(64),
    recipient VARCHAR(64),
    content TEXT,
    created_at BIGINT,
    delivered_at BIGINT,
    status VARCHAR(32)
);

-- 会话表
CREATE TABLE sessions (
    id VARCHAR(64) PRIMARY KEY,
    type VARCHAR(32),  -- 'single' / 'group'
    created_at BIGINT,
    updated_at BIGINT
);

-- 会话成员表
CREATE TABLE session_members (
    session_id VARCHAR(64),
    agent_id VARCHAR(64),
    joined_at BIGINT,
    PRIMARY KEY (session_id, agent_id)
);

-- Agent能力表
CREATE TABLE capabilities (
    id VARCHAR(64) PRIMARY KEY,
    agent_id VARCHAR(64),
    name VARCHAR(128),
    description TEXT,
    schema TEXT
);
```

### 3.2 Redis设计

```
Key设计:
  presence:{agent_id}        - 在线状态
  session:{session_id}       - 会话数据
  offline:{agent_id}         - 离线消息队列
  typing:{session_id}        - 正在输入状态
```

---

## 四、API设计

### 4.1 HTTP API

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/agents` | POST | 注册Agent |
| `/api/v1/agents/{did}` | GET | 获取Agent信息 |
| `/api/v1/agents/search` | GET | 搜索Agent |
| `/api/v1/sessions` | POST | 创建会话 |
| `/api/v1/messages/{message_id}` | GET | 获取消息历史 |

### 4.2 WebSocket消息

| 消息类型 | 方向 | 描述 |
|----------|------|------|
| `connect` | C→S | 连接 |
| `connected` | S→C | 连接确认 |
| `message` | C↔S | 消息 |
| `presence` | C→S | 状态变更 |
| `typing` | C↔S | 正在输入 |
| `receipt` | S→C | 送达回执 |

---

## 五、安全设计

### 5.1 身份认证

```
流程:
1. Agent连接时发送DID
2. 服务器生成挑战
3. Agent使用私钥签名
4. 服务器验证签名
5. 连接建立
```

### 5.2 消息签名 (可选)

```
消息签名:
{
    "message_id": "uuid",
    "sender": "did:wba:agent:a",
    "content": "Hello",
    "signature": "base64_signature"
}
```

---

## 六、部署设计

### 6.1 MVP部署

```
单服务器部署:

┌─────────────────────────────────────┐
│          Web服务器 (Nginx)           │
│          (端口 80/443)              │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│        Application Server            │
│        (FastAPI + WebSocket)        │
│        (端口 8000)                  │
└─────────────────────────────────────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
┌───▼────┐               ┌───▼────┐
│ Redis  │               │SQLite  │
│ 缓存   │               │ 数据库  │
└────────┘               └────────┘
```

### 6.2 扩展计划

```
v2.0 多服务器:

          Nginx LB
             │
    ┌────────┼────────┐
    │        │        │
 Server1  Server2  Server3
    │        │        │
    └────────┼────────┘
             │
      Redis Cluster
```

---

## 七、测试计划

### 7.1 单元测试

| 模块 | 测试用例 |
|------|----------|
| Gateway | 连接/断连/消息 |
| Message | 发送/接收/存储 |
| Presence | 在线/离线/心跳 |
| Discovery | 注册/搜索 |

### 7.2 集成测试

```
场景:
1. Agent连接流程
2. 发送消息流程
3. 群聊流程
4. 离线消息流程
```

### 7.3 性能测试

```
指标:
- 并发连接: 1000+
- 消息吞吐量: 1000+/秒
- 延迟: <100ms
```

---

## 八、版本规划

### 8.1 MVP版本 (v0.1)

```
目标: 基础功能验证
时间: 3个月
功能: 单聊 + 在线状态 + 基础发现
```

### 8.2 v1.0版本

```
目标: 生产可用
时间: 6个月
功能: 完整群组 + 消息搜索 + 性能优化
```

---

*文档状态: 初稿待评审*
