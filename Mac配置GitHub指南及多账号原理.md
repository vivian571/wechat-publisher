# Mac 电脑配置 GitHub 账号指南与多账号原理解析

## 第一部分：Mac 电脑配置 GitHub 账号 (SSH 方式)

在 Mac 上配置 GitHub 最推荐使用 **SSH 密钥** 方式，配置一次后即可免密提交代码。请打开 Mac 自带的 **终端 (Terminal)** 应用，按以下步骤操作：

### 1. 检查/配置 Git 用户信息
告诉 Git 你是谁（这将显示在你的提交记录中）：
```bash
# 1. 设置用户名（用你的 GitHub 用户名）
git config --global user.name "你的GitHub用户名"

# 2. 设置邮箱（必须是你 GitHub 注册的邮箱）
git config --global user.email "你的GitHub邮箱@example.com"
```

### 2. 生成 SSH 密钥
```bash
# 执行生成命令（一直按回车即可，无需设置密码）
ssh-keygen -t ed25519 -C "你的GitHub邮箱@example.com"
```
*执行完毕后，系统会提示密钥已保存到 `/Users/你的用户名/.ssh/id_ed25519`*

### 3. 获取并复制公钥
在终端输入以下命令查看公钥内容：
```bash
cat ~/.ssh/id_ed25519.pub
```
**选中并复制** 输出的以 `ssh-ed25519` 开头的一长串字符。

### 4. 在 GitHub 网站添加公钥
1.  登录 GitHub 网页。
2.  点击右上角头像 -> **Settings**。
3.  左侧菜单点 **SSH and GPG keys** -> 点击 **New SSH key**。
4.  **Title** 随便填（如 "MyMacBook"）。
5.  **Key** 粘贴刚才复制的内容。
6.  点击 **Add SSH key**。

### 5. 验证连接
回到终端输入：
```bash
ssh -T git@github.com
```
如果看到提示 `Are you sure you want to continue connecting (yes/no/[fingerprint])?`，输入 `yes` 并回车。
看到 **"Hi [你的用户名]! You've successfully authenticated..."** 即表示配置成功！

---

## 第二部分：为什么可以同时登录 Google 和 GitHub？

这其实不是操作系统的功能（Windows 或 Mac），而是**互联网服务的基本原理**。就像你可以同时在一个浏览器里通过两个标签页分别登录“微信网页版”和“淘宝”一样。

### 核心原因：

1.  **独立的服务商**：
    *   **Google** 是 Alphabet 公司的服务。
    *   **GitHub** 是微软（Microsoft）旗下的代码托管平台。
    *   它们是两套完全独立的数据库和账号体系，互不排斥。

2.  **浏览器的“饼干” (Cookies) 隔离**：
    *   当你登录 Google 时，浏览器保存了一个属于 `google.com` 的 Cookie（通行证）。
    *   当你登录 GitHub 时，浏览器保存了一个属于 `github.com` 的 Cookie。
    *   浏览器会自动管理这些通行证，访问 Google 发送 Google 的证件，访问 GitHub 发送 GitHub 的证件。它们互不干扰。

### Mac 也可以吗？
**当然可以。** 在 Mac 上，只要你的网络环境能够访问这两个网站，你可以随时开启两个标签页，左边用 Google 搜索，右边在 GitHub 提交代码，这与 Windows 的体验是完全一致的。

> **💡 特别提示**：
> 唯一可能产生“必须二选一”错觉的情况是**网络代理冲突**。如果在 Mac 上遇到“开了这个打不开那个”的情况，通常是代理软件的规则配置问题（PAC模式 vs 全局模式），而不是账号体系的冲突。
