# Agent通信协议规范文档

**版本**: v1.0
**日期**: 2026-02-28

---

## 一、协议概述

### 1.1 协议定义

| 项目 | 说明 |
|------|------|
| 协议名称 | Agent Message Protocol (AMP) |
| 版本 | 1.0 |
| 协议类型 | 应用层协议 |

### 1.2 协议目标

- 为Agent提供标准化通信能力
- 支持百亿级Agent规模
- 确保消息可靠传输

---

## 二、消息格式

### 2.1 JSON消息格式

```json
{
    "msg_id": "uuid-string",
    "session_id": "session-uuid",
    "sender": "did:wba:agent:sender",
    "recipient": "did:wba:agent:recipient",
    "type": "message",
    "content": {
        "type": "text",
        "body": "消息内容"
    },
    "timestamp": 1700000000,
    "sequence": 1,
    "metadata": {}
}
```

### 2.2 消息字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| msg_id | string | 是 | 消息唯一ID |
| session_id | string | 是 | 会话ID |
| sender | string | 是 | 发送者DID |
| recipient | string | 是 | 接收者DID |
| type | string | 是 | 消息类型 |
| content | object | 是 | 消息内容 |
| timestamp | int | 是 | 时间戳(秒) |
| sequence | int | 是 | 序列号 |
| metadata | object | 否 | 扩展元数据 |

---

## 三、消息类型

### 3.1 消息类型枚举

| 类型值 | 说明 |
|--------|------|
| `message` | 文本/媒体消息 |
| `system` | 系统消息 |
| `typing` | 正在输入 |
| `presence` | 状态变更 |
| `receipt` | 送达回执 |

### 3.2 内容类型

| 类型值 | 说明 |
|--------|------|
| `text` | 文本消息 |
| `image` | 图片消息 |
| `file` | 文件消息 |
| `code` | 代码消息 |
| `action` | 操作消息 |

---

## 四、传输协议

### 4.1 WebSocket消息

#### 4.1.1 消息帧格式

```
WebSocket Frame:
{
    "opcode": 1 (text),
    "payload": JSON string
}
```

#### 4.1.2 连接流程

```
Client                                              Server
  |                                                    |
  |--------------- WebSocket Connect ----------------->|
  |                                                    |
  |<-------------- WSS Handshake ---------------------|
  |                                                    |
  |-------------- Connect Message ------------------->|
  |  {                                                 |
  |    "type": "connect",                             |
  |    "did": "did:wba:agent:a",                     |
  |    "challenge": "xxx"                            |
  |  }                                                 |
  |                                                    |
  |<------------- Connected ---------------------------|
  |  {                                                 |
  |    "type": "connected",                           |
  |    "session_id": "ws_xxx"                        |
  |  }                                                 |
  |                                                    |
```

### 4.2 HTTP API

#### 4.2.1 认证头

```
Authorization: AMP-Signature signature="xxx",timestamp="xxx"
```

---

## 五、DID身份

### 5.1 DID格式

```
did:wba:agent:{identifier}

示例:
did:wba:agent:abc123
did:wba:agent:agent-001
```

### 5.2 身份验证流程

```
1. Agent连接时发送DID
2. Server生成随机挑战
3. Agent使用私钥签名挑战
4. Server通过DID文档获取公钥
5. 验证签名
6. 验证通过，连接建立
```

---

## 六、Agent能力描述 (Agent Card)

### 6.1 Agent Card格式

```json
{
    "did": "did:wba:agent:xxx",
    "name": "MyAgent",
    "description": "Agent描述",
    "capabilities": [
        {
            "name": "web_search",
            "description": "网页搜索能力",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                }
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "results": {"type": "array"}
                }
            }
        }
    ],
    "endpoints": {
        "http": "https://agent.example.com/api",
        "ws": "wss://agent.example.com/ws"
    },
    "public_key": "base64_key",
    "expires": 1700000000
}
```

### 6.2 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| did | string | Agent DID |
| name | string | Agent名称 |
| description | string | Agent描述 |
| capabilities | array | 能力列表 |
| endpoints | object | 端点列表 |
| public_key | string | 公钥 |
| expires | int | 过期时间 |

---

## 七、会话协议

### 7.1 会话类型

| 类型 | 说明 |
|------|------|
| `single` | 单聊 |
| `group` | 群聊 |

### 7.2 会话消息顺序

```
消息顺序保证:
1. 每条消息有sequence序号
2. 接收方按sequence排序
3. 缺失消息请求重传
```

---

## 八、消息可靠性

### 8.1 送达回执

```
状态值:
- sending: 发送中
- sent: 已发送
- delivered: 已送达
- read: 已读
- failed: 失败
```

### 8.2 重试机制

```
重试规则:
- 发送失败后重试3次
- 重试间隔: 1s, 5s, 30s
- 重试失败标记为failed
```

---

## 九、安全协议

### 9.1 TLS传输加密

```
所有连接必须使用TLS 1.3
```

### 9.2 消息签名 (可选)

```json
{
    "msg_id": "xxx",
    "sender": "did:wba:agent:a",
    "content": {...},
    "signature": "base64_signature"
}
```

---

## 十、错误处理

### 10.1 错误消息格式

```json
{
    "type": "error",
    "code": 1000,
    "message": "错误描述",
    "detail": {}
}
```

### 10.2 错误码

| 错误码 | 说明 |
|--------|------|
| 1000 | 参数错误 |
| 1001 | 消息格式错误 |
| 2000 | 认证失败 |
| 2001 | 权限不足 |
| 3000 | 资源不存在 |
| 4000 | 服务器错误 |

---

## 十一、协议扩展

### 11.1 自定义消息类型

```
扩展格式:
{
    "type": "custom:xxx",
    "content": {...}
}
```

### 11.2 元数据扩展

```
metadata字段用于扩展:
{
    "metadata": {
        "custom_field": "value"
    }
}
```

---

## 附录

### A. 消息示例

**文本消息**:
```json
{
    "msg_id": "msg_001",
    "session_id": "sess_001",
    "sender": "did:wba:agent:a",
    "recipient": "did:wba:agent:b",
    "type": "message",
    "content": {
        "type": "text",
        "body": "你好"
    },
    "timestamp": 1700000000,
    "sequence": 1
}
```

**系统消息**:
```json
{
    "msg_id": "msg_002",
    "session_id": "sess_001",
    "type": "system",
    "content": {
        "type": "system",
        "body": "Agent A加入了群聊"
    },
    "timestamp": 1700000001
}
```

---

*协议版本: 1.0*
*最后更新: 2026-02-28*
