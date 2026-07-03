# 第12节: 网络编程1
# 内容: 计算机网络体系、TCP系列网络编程

import socket
import threading
import time

# --- 1. TCP 服务器端 --- 
print("--- 1. TCP 服务器端示例 ---")

def handle_client(client_socket, client_address):
    """处理单个客户端连接的函数"""
    print(f"[服务器] 接受来自 {client_address} 的连接")
    try:
        while True:
            # 接收数据 (最多1024字节)
            data = client_socket.recv(1024)
            if not data:
                print(f"[服务器] 客户端 {client_address} 断开连接")
                break
            
            message = data.decode('utf-8')
            print(f"[服务器] 收到来自 {client_address} 的消息: {message}")
            
            # 发送响应
            response = f"服务器收到: {message}".encode('utf-8')
            client_socket.sendall(response)
            print(f"[服务器] 已向 {client_address} 发送响应")
            
    except ConnectionResetError:
        print(f"[服务器] 客户端 {client_address} 强制断开连接")
    except Exception as e:
        print(f"[服务器] 处理客户端 {client_address} 时出错: {e}")
    finally:
        client_socket.close()
        print(f"[服务器] 关闭与 {client_address} 的连接")

def start_tcp_server(host='127.0.0.1', port=9999):
    """启动 TCP 服务器"""
    # 创建 socket 对象 (AF_INET: IPv4, SOCK_STREAM: TCP)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 绑定地址和端口
    try:
        server_socket.bind((host, port))
        print(f"[服务器] 成功绑定到 {host}:{port}")
    except OSError as e:
        print(f"[服务器] 绑定失败: {e} (端口可能已被占用)")
        return

    # 开始监听连接 (backlog=5 表示允许最多5个连接排队)
    server_socket.listen(5)
    print(f"[服务器] 开始监听端口 {port}...")

    try:
        while True:
            # 接受客户端连接 (阻塞等待)
            client_socket, client_address = server_socket.accept()
            
            # 为每个客户端创建一个新线程来处理
            client_handler = threading.Thread(
                target=handle_client, 
                args=(client_socket, client_address)
            )
            client_handler.start()
            
    except KeyboardInterrupt:
        print("\n[服务器] 检测到 Ctrl+C，正在关闭服务器...")
    finally:
        server_socket.close()
        print("[服务器] 服务器套接字已关闭")

# 启动服务器 (在一个单独的线程中，以便后续客户端代码可以运行)
# 注意：实际应用中服务器通常是独立运行的进程
server_thread = threading.Thread(target=start_tcp_server)
server_thread.daemon = True # 设置为守护线程，主程序退出时它也退出
server_thread.start()

print("[主程序] TCP 服务器线程已启动，等待几秒让服务器初始化...")
time.sleep(2) # 给服务器一点启动时间

# --- 2. TCP 客户端 --- 
print("\n--- 2. TCP 客户端示例 ---")

def start_tcp_client(server_host='127.0.0.1', server_port=9999):
    """启动 TCP 客户端并与服务器交互"""
    # 创建 socket 对象
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # 连接服务器
        print(f"[客户端] 尝试连接到服务器 {server_host}:{server_port}...")
        client_socket.connect((server_host, server_port))
        print("[客户端] 连接成功!")
        
        # 发送数据
        messages = ["你好，服务器!", "这是第二条消息", "quit"]
        for message in messages:
            print(f"[客户端] 发送消息: {message}")
            client_socket.sendall(message.encode('utf-8'))
            
            # 接收响应
            response = client_socket.recv(1024)
            print(f"[客户端] 收到响应: {response.decode('utf-8')}")
            time.sleep(1) # 等待一下再发下一条
            
            if message == "quit":
                break
                
    except ConnectionRefusedError:
        print(f"[客户端] 连接失败: 服务器 {server_host}:{server_port} 拒绝连接。请确保服务器正在运行。")
    except Exception as e:
        print(f"[客户端] 发生错误: {e}")
    finally:
        # 关闭连接
        client_socket.close()
        print("[客户端] 连接已关闭")

# 运行客户端
start_tcp_client()

print("\nTCP 客户端示例结束。服务器线程仍在后台运行（如果是守护线程，将在主程序结束时停止）。")

# 等待服务器线程中的打印信息显示完全 (非必要，仅为演示)
time.sleep(3)

print("\n第12节示例代码结束。")