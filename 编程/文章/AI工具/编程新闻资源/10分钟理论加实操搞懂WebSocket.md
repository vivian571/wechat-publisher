# 10分钟理论+实操搞懂WebSocket，通信不再难！

**<font color='red'>还在用HTTP轮询？太LOW了！</font>**

每次都要不停地发请求问服务器"有新消息吗？有新消息吗？"，这不是很烦人吗？

网页想实时聊天、游戏操作、股票行情，靠HTTP真的很尴尬！

**<font color='blue'>WebSocket来了，通信问题一次性解决！</font>**

## 一、WebSocket是什么？

**<font color='green'>WebSocket就是一种网络通信协议，让浏览器和服务器之间建立持久连接。</font>**

它的特点超级棒：

**全双工通信**：双方可以同时收发数据，不用排队等待。

**持久连接**：建立一次连接，就能一直用，不用反复连接。

**实时性强**：消息到达延迟极低，毫秒级响应。

**更少的控制开销**：连接建立后，数据传输很轻量，不带HTTP头。

## 二、为啥要用WebSocket？

**<font color='red'>HTTP协议的痛点太明显了！</font>**

**请求-响应模式**：客户端必须先发请求，服务器才能回应，服务器不能主动推送。

**无状态**：每次请求都是独立的，服务器不记得你是谁。

**头信息冗余**：每次请求都带一大堆HTTP头，浪费带宽。

看看这些场景，HTTP多尴尬：

**<font color='purple'>聊天应用</font>**：小明发消息给你，服务器知道了，但必须等你发请求来问才能告诉你。

**<font color='purple'>在线游戏</font>**：对手移动了，你必须不停地问服务器"有更新吗？"才能知道。

**<font color='purple'>股票行情</font>**：价格变了，你必须刷新页面或者用轮询才能看到最新价格。

## 三、WebSocket工作原理

**<font color='blue'>WebSocket连接建立超简单！</font>**

**握手阶段**：

1. 客户端发送HTTP请求，带特殊头部：`Upgrade: websocket`

2. 服务器同意升级，回复状态码101

3. 握手成功，HTTP连接升级为WebSocket连接

**数据传输阶段**：

双方可以随时发送消息，不需要请求-响应模式。

消息有个简单的帧结构，支持文本和二进制数据。

## 四、实操：搭建WebSocket服务器（Node.js）

**<font color='blue'>服务端代码超简单，看完就会！</font>**

```javascript
// 安装依赖：npm install ws
const WebSocket = require('ws');

// 创建WebSocket服务器，监听8080端口
const wss = new WebSocket.Server({ port: 8080 });

// 监听连接事件
wss.on('connection', function connection(ws) {
  console.log('有新客户端连接了！');
  
  // 监听客户端发来的消息
  ws.on('message', function incoming(message) {
    console.log('收到消息：', message.toString());
    
    // 广播消息给所有客户端
    wss.clients.forEach(function each(client) {
      if (client.readyState === WebSocket.OPEN) {
        client.send(`服务器收到了：${message}`);
      }
    });
  });
  
  // 发送欢迎消息
  ws.send('欢迎连接WebSocket服务器！');
});

console.log('WebSocket服务器已启动，监听端口8080');
```

**<font color='green'>就这么几行代码，一个实时通信服务器就搞定了！</font>**

## 五、实操：WebSocket客户端（浏览器）

**<font color='blue'>客户端代码更简单，三行搞定！</font>**

```html
<!DOCTYPE html>
<html>
<head>
  <title>WebSocket客户端</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
    #messages { height: 300px; overflow-y: scroll; border: 1px solid #ccc; margin-bottom: 10px; padding: 10px; }
    #input { width: 80%; padding: 5px; }
    button { padding: 5px 10px; }
  </style>
</head>
<body>
  <h1>WebSocket聊天室</h1>
  <div id="messages"></div>
  <input type="text" id="input" placeholder="输入消息..."/>
  <button onclick="sendMessage()">发送</button>

  <script>
    // 创建WebSocket连接
    const socket = new WebSocket('ws://localhost:8080');
    const messagesDiv = document.getElementById('messages');
    const input = document.getElementById('input');
    
    // 连接建立时触发
    socket.onopen = function(event) {
      addMessage('系统', '连接已建立！');
    };
    
    // 收到消息时触发
    socket.onmessage = function(event) {
      addMessage('服务器', event.data);
    };
    
    // 连接关闭时触发
    socket.onclose = function(event) {
      addMessage('系统', '连接已关闭');
    };
    
    // 发生错误时触发
    socket.onerror = function(error) {
      addMessage('错误', '连接出错了！');
    };
    
    // 发送消息
    function sendMessage() {
      const message = input.value;
      if (message) {
        socket.send(message);
        addMessage('我', message);
        input.value = '';
      }
    }
    
    // 在页面上添加消息
    function addMessage(sender, message) {
      const messageElement = document.createElement('div');
      messageElement.textContent = `${sender}: ${message}`;
      messagesDiv.appendChild(messageElement);
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
    
    // 按回车键发送消息
    input.addEventListener('keypress', function(event) {
      if (event.key === 'Enter') {
        sendMessage();
      }
    });
  </script>
</body>
</html>
```

## 六、WebSocket vs HTTP对比

**<font color='red'>一图看懂两者区别！</font>**

**HTTP通信模式**：
- 客户端必须先发请求
- 服务器只能回应，不能主动推送
- 每次都要建立新连接
- 每次都带HTTP头，浪费流量

**WebSocket通信模式**：
- 客户端和服务器都能主动发消息
- 建立一次连接，持续通信
- 传输数据量小，只有帧头和数据
- 实时性强，延迟低

## 七、WebSocket应用场景

**<font color='green'>这些场景用WebSocket简直完美！</font>**

**聊天应用**：微信网页版、在线客服系统。

**协同编辑**：多人同时编辑文档，如腾讯文档。

**实时游戏**：网页小游戏、棋牌游戏。

**股票行情**：实时更新价格、K线图。

**体育赛事**：实时比分、直播评论。

**物联网设备**：实时监控、远程控制。

## 八、WebSocket注意事项

**<font color='orange'>用好WebSocket，这些坑要避开！</font>**

**连接可能断开**：网络不稳定时要自动重连。

**安全问题**：用wss://（加密）而不是ws://。

**负载均衡**：大型应用需要考虑分布式部署。

**心跳机制**：定期发送心跳包，保持连接活跃。

**兼容性**：老旧浏览器可能不支持，需要降级方案。

## 九、总结

**<font color='blue'>WebSocket就是这么简单好用！</font>**

**建立连接**：一次HTTP握手，升级为WebSocket。

**双向通信**：服务器和客户端都能随时发消息。

**实时性强**：延迟低，适合实时应用。

**使用简单**：几行代码就能实现实时通信。

**<font color='red'>还在用HTTP轮询？快换WebSocket吧！</font>**

你的应用需要实时通信功能吗？WebSocket绝对是你的不二之选！