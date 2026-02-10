# 零基础教程：如何编写自己的第一个MCP插件

> 随着AI技术的发展，MCP（Modular Capability Provider）作为一种强大的AI能力扩展机制，正在受到越来越多开发者的关注。本文将带您从零开始，一步步学习如何创建自己的第一个MCP插件，让您的AI助手拥有更强大的能力。

## 什么是MCP？

MCP（Modular Capability Provider）是一种模块化能力提供者，它允许开发者为AI助手（如GPT、Claude等）扩展额外的功能。通过MCP插件，AI助手可以：

- 访问特定的数据库或API
- 执行复杂的计算
- 与外部系统交互
- 获取实时信息
- 执行特定领域的专业任务

简单来说，MCP就像是AI助手的"超能力插件"，让AI能够突破原有的限制，完成更加复杂和专业的任务。

## 准备工作

在开始编写MCP插件之前，您需要准备以下内容：

1. **Node.js环境**：确保您已安装Node.js（建议v14.0.0或更高版本）
2. **开发工具**：推荐使用VS Code作为代码编辑器
3. **MCP SDK**：我们将使用官方提供的SDK来简化开发过程
4. **基本的JavaScript/TypeScript知识**：MCP插件主要使用这些语言开发

## 第一步：安装MCP SDK

首先，创建一个新的项目文件夹，并初始化npm项目：

```bash
mkdir my-first-mcp
cd my-first-mcp
npm init -y
```

然后，安装MCP SDK：

```bash
npm install @microsoft/mcp-sdk
```

## 第二步：创建插件基础结构

MCP插件通常包含以下几个关键文件：

1. `manifest.json`：插件的配置文件，定义插件的基本信息和能力
2. `index.js`：插件的入口文件，实现插件的核心功能
3. `schema.json`：定义插件API的输入输出格式

让我们先创建`manifest.json`文件：

```json
{
  "schema_version": "v1",
  "name_for_human": "我的第一个MCP插件",
  "name_for_model": "myFirstMCP",
  "description_for_human": "这是我创建的第一个MCP插件，用于演示基本功能",
  "description_for_model": "这个插件提供了一个简单的计算器功能，可以执行基本的数学运算",
  "auth": {
    "type": "none"
  },
  "api": {
    "type": "openapi",
    "url": "http://localhost:3000/openapi.yaml"
  },
  "logo_url": "https://example.com/logo.png",
  "contact_email": "support@example.com",
  "legal_info_url": "https://example.com/legal"
}
```

## 第三步：定义API架构

接下来，我们需要创建`openapi.yaml`文件，定义插件的API结构：

```yaml
openapi: 3.0.0
info:
  title: 简单计算器MCP
  description: 一个提供基本数学运算的MCP插件
  version: 1.0.0
servers:
  - url: http://localhost:3000
paths:
  /calculate:
    post:
      summary: 执行数学计算
      operationId: calculate
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - operation
                - num1
                - num2
              properties:
                operation:
                  type: string
                  enum: [add, subtract, multiply, divide]
                  description: 要执行的数学运算
                num1:
                  type: number
                  description: 第一个数字
                num2:
                  type: number
                  description: 第二个数字
      responses:
        '200':
          description: 成功的计算结果
          content:
            application/json:
              schema:
                type: object
                properties:
                  result:
                    type: number
                    description: 计算结果
        '400':
          description: 无效的输入参数
```

## 第四步：实现插件功能

现在，让我们创建`index.js`文件，实现插件的核心功能：

```javascript
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const yaml = require('js-yaml');
const fs = require('fs');
const path = require('path');

// 创建Express应用
const app = express();
app.use(bodyParser.json());
app.use(cors());

// 提供OpenAPI规范
app.get('/openapi.yaml', (req, res) => {
  const openApiPath = path.join(__dirname, 'openapi.yaml');
  const yamlContent = fs.readFileSync(openApiPath, 'utf8');
  res.setHeader('Content-Type', 'text/yaml');
  res.send(yamlContent);
});

// 实现计算器API
app.post('/calculate', (req, res) => {
  const { operation, num1, num2 } = req.body;
  
  if (!operation || num1 === undefined || num2 === undefined) {
    return res.status(400).json({ error: '缺少必要参数' });
  }
  
  let result;
  
  switch (operation) {
    case 'add':
      result = num1 + num2;
      break;
    case 'subtract':
      result = num1 - num2;
      break;
    case 'multiply':
      result = num1 * num2;
      break;
    case 'divide':
      if (num2 === 0) {
        return res.status(400).json({ error: '除数不能为零' });
      }
      result = num1 / num2;
      break;
    default:
      return res.status(400).json({ error: '不支持的操作' });
  }
  
  res.json({ result });
});

// 启动服务器
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`MCP插件服务器运行在端口 ${PORT}`);
});
```

别忘了安装所需的依赖：

```bash
npm install express body-parser cors js-yaml
```

## 第五步：测试您的MCP插件

现在，让我们启动插件服务器并进行测试：

```bash
node index.js
```

您可以使用curl或Postman等工具测试您的API：

```bash
curl -X POST http://localhost:3000/calculate \
  -H "Content-Type: application/json" \
  -d '{"operation":"add","num1":5,"num2":3}'
```

如果一切正常，您应该会收到类似以下的响应：

```json
{"result":8}
```

## 第六步：将MCP插件与AI助手集成

要将您的MCP插件与AI助手集成，您需要：

1. 确保您的插件服务器可以从互联网访问（可以使用ngrok等工具进行临时暴露）
2. 在AI平台（如OpenAI、Anthropic等）上注册您的插件
3. 按照平台的指南完成集成过程

例如，使用ngrok暴露您的本地服务器：

```bash
ngrok http 3000
```

然后，使用ngrok提供的URL更新您的manifest.json和openapi.yaml中的服务器地址。

## 进阶技巧

### 1. 添加身份验证

对于需要保护的API，您可以添加身份验证机制：

```json
// 在manifest.json中
"auth": {
  "type": "oauth2",
  "client_url": "https://example.com/oauth",
  "scope": "read write",
  "authorization_url": "https://example.com/oauth/authorize",
  "authorization_content_type": "application/json",
  "verification_tokens": {
    "openai": "your-verification-token"
  }
}
```

### 2. 使用TypeScript提高代码质量

将项目转换为TypeScript可以提供更好的类型检查和开发体验：

```bash
npm install typescript @types/express @types/node --save-dev
```

创建`tsconfig.json`：

```json
{
  "compilerOptions": {
    "target": "es2018",
    "module": "commonjs",
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true
  },
  "include": ["src/**/*"]
}
```

### 3. 添加更多功能

您可以扩展您的MCP插件，添加更多功能，例如：

- 连接数据库
- 集成第三方API
- 实现文件处理
- 添加缓存机制
- 实现更复杂的业务逻辑

## 常见问题与解决方案

1. **插件无法被AI助手发现**
   - 检查manifest.json格式是否正确
   - 确保服务器可以从互联网访问

2. **API调用失败**
   - 检查请求和响应格式是否符合OpenAPI规范
   - 查看服务器日志以获取详细错误信息

3. **性能问题**
   - 添加缓存机制
   - 优化数据库查询
   - 考虑使用更高效的算法

## 结语

恭喜您！您已经成功创建了自己的第一个MCP插件。这只是开始，随着您对MCP开发的深入理解，您可以创建更加复杂和强大的插件，为AI助手赋予更多能力。

记住，优秀的MCP插件应该：
- 解决特定的问题
- 提供清晰的API
- 具有良好的性能
- 保持安全性
- 提供友好的错误处理

希望本教程对您有所帮助，祝您在MCP插件开发的道路上取得成功！

## 参考资源

- [MCP官方文档](https://example.com/mcp-docs)
- [OpenAPI规范](https://swagger.io/specification/)
- [Express.js文档](https://expressjs.com/)
- [Node.js最佳实践](https://github.com/goldbergyoni/nodebestpractices)
