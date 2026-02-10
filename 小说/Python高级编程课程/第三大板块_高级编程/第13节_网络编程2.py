# 第13节: 网络编程2
# 内容: TCP并发方案、UDP系列网络编程

import socket
import threading
import socketserver
import time

# --- 1. TCP 并发方案 (使用 socketserver) ---
print("--- 1. TCP 并发方案 (socketserver) 示例 ---")

# 1.1 定义请求处理器类
class MyTCPHandler(socketserver.BaseRequestHandler):
    """自定义的 TCP 请求处理器"""
    def handle(self):
        # self.request 就是客户端的 socket 连接
        client_address = self.client_address
        print(f"[SocketServer] 接受来自 {client_address} 的连接")
        try:
            while True:
                data = self.request.recv(1024)
                if not data:
                    print(f"[SocketServer] 客户端 {client_address} 断开连接")
                    break
                message = data.decode('utf-8').strip()
                print(f"[SocketServer] 收到来自 {client_address} 的消息: {message}")
                response = f"服务器 (SocketServer) 收到: {message}".encode('utf-8')
                self.request.sendall(response)
                print(f"[SocketServer] 已向 {client_address} 发送响应")
        except ConnectionResetError:
            print(f"[SocketServer] 客户端 {client_address} 强制断开连接")
        except Exception as e:
            print(f"[SocketServer] 处理客户端 {client_address} 时出错: {e}")
        finally:
            print(f"[SocketServer] 关闭与 {client_address} 的连接处理")
            # 连接关闭由 socketserver 框架管理，通常不需要手动关闭 self.request

# 1.2 创建并运行服务器 (使用 ThreadingMixIn 实现多线程并发)
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """支持多线程并发的 TCP 服务器"""
    pass # Mixin 提供了并发处理能力

HOST, PORT = "127.0.0.1", 9998 # 使用不同于上一节的端口

def start_socket_server():
    print(f"[SocketServer] 准备在 {HOST}:{PORT} 启动 TCP 服务器...")
    try:
        # 创建服务器实例，绑定地址和处理器
        server = ThreadedTCPServer((HOST, PORT), MyTCPHandler)
        
        # 启动服务器 (在新线程中运行，以便主程序继续)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True # 主线程退出时服务器线程也退出
        server_thread.start()
        print(f"[SocketServer] 服务器已在线程 {server_thread.name} 中启动，正在监听...")
        
        # 让主线程保持运行一段时间，或者等待特定条件
        # time.sleep(60) # 例如，运行60秒
        # server.shutdown() # 关闭服务器
        # server.server_close() # 清理资源
        # print("[SocketServer] 服务器已关闭")
        return server # 返回服务器对象以便后续可以关闭
    except OSError as e:
        print(f"[SocketServer] 启动失败: {e} (端口 {PORT} 可能已被占用)")
        return None
    except Exception as e:
        print(f"[SocketServer] 启动时发生未知错误: {e}")
        return None

# 启动 SocketServer 服务器
socket_server_instance = start_socket_server()

if socket_server_instance:
    print("[主程序] SocketServer 服务器线程已启动，等待几秒...")
    time.sleep(2)

    # 可以用上一节的 TCP 客户端连接这个服务器进行测试
    # start_tcp_client(server_port=9998)
    print("[主程序] 可以使用 TCP 客户端连接 127.0.0.1:9998 进行测试。")
else:
    print("[主程序] SocketServer 未能启动。")

print("TCP 并发方案 (socketserver) 示例结束。\n")

# --- 2. UDP 系列网络编程 --- 
print("--- 2. UDP 网络编程示例 ---")

# 2.1 UDP 服务器端
def start_udp_server(host='127.0.0.1', port=9997):
    print(f"[UDP 服务器] 准备在 {host}:{port} 启动 UDP 服务器...")
    # 创建 UDP socket (SOCK_DGRAM)
    udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        udp_server_socket.bind((host, port))
        print(f"[UDP 服务器] 成功绑定到 {host}:{port}")
        print(f"[UDP 服务器] 开始监听端口 {port}...")
        
        while True:
            # 接收数据 (recvfrom 返回数据和发送方地址)
            data, client_address = udp_server_socket.recvfrom(1024)
            if not data:
                continue # UDP 是无连接的，没有明确的断开
                
            message = data.decode('utf-8')
            print(f"[UDP 服务器] 收到来自 {client_address} 的消息: {message}")
            
            # 发送响应 (sendto 需要指定目标地址)
            response = f"UDP 服务器收到: {message}".encode('utf-8')
            udp_server_socket.sendto(response, client_address)
            print(f"[UDP 服务器] 已向 {client_address} 发送响应")
            
            # 如果收到特定消息则退出 (仅为示例)
            if message.lower() == 'exit':
                print("[UDP 服务器] 收到退出指令，关闭服务器。")
                break
                
    except OSError as e:
        print(f"[UDP 服务器] 绑定失败: {e} (端口 {port} 可能已被占用)")
    except KeyboardInterrupt:
        print("\n[UDP 服务器] 检测到 Ctrl+C，正在关闭服务器...")
    except Exception as e:
        print(f"[UDP 服务器] 发生错误: {e}")
    finally:
        udp_server_socket.close()
        print("[UDP 服务器] UDP 套接字已关闭")

# 在新线程中启动 UDP 服务器
udp_server_thread = threading.Thread(target=start_udp_server)
udp_server_thread.daemon = True
udp_server_thread.start()

print("[主程序] UDP 服务器线程已启动，等待几秒...")
time.sleep(2)

# 2.2 UDP 客户端
def start_udp_client(server_host='127.0.0.1', server_port=9997):
    print(f"[UDP 客户端] 准备向 {server_host}:{server_port} 发送 UDP 数据...")
    # 创建 UDP socket
    udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        messages = ["Hello UDP Server!", "第二条 UDP 消息", "exit"]
        for message in messages:
            print(f"[UDP 客户端] 发送消息: {message}")
            # 发送数据到服务器地址
            udp_client_socket.sendto(message.encode('utf-8'), (server_host, server_port))
            
            # 尝试接收响应 (设置超时，因为 UDP 不保证响应)
            try:
                udp_client_socket.settimeout(2.0) # 等待2秒
                response_data, server_address = udp_client_socket.recvfrom(1024)
                print(f"[UDP 客户端] 收到来自 {server_address} 的响应: {response_data.decode('utf-8')}")
            except socket.timeout:
                print("[UDP 客户端] 等待响应超时")
            
            time.sleep(1)
            
    except Exception as e:
        print(f"[UDP 客户端] 发生错误: {e}")
    finally:
        udp_client_socket.close()
        print("[UDP 客户端] UDP 套接字已关闭")

# 运行 UDP 客户端
start_udp_client()

print("\nUDP 网络编程示例结束。")

# 等待服务器线程中的打印信息显示完全 (非必要，仅为演示)
time.sleep(3)

# 如果需要，可以手动停止 SocketServer
# if socket_server_instance:
#     print("[主程序] 准备关闭 SocketServer...")
#     socket_server_instance.shutdown() # 请求停止 serve_forever 循环
#     socket_server_instance.server_close() # 关闭服务器套接字
#     print("[主程序] SocketServer 已关闭。")

print("\n第13节示例代码结束。")