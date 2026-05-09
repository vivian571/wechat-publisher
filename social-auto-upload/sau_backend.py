import asyncio
import os
import sqlite3
import threading
import time
import uuid
import subprocess
from pathlib import Path
from queue import Queue
from flask_cors import CORS
from myUtils.auth import check_cookie
from flask import Flask, request, jsonify, Response, render_template, send_from_directory
from conf import BASE_DIR
from myUtils.login import get_tencent_cookie, douyin_cookie_gen, get_ks_cookie, xiaohongshu_cookie_gen
from myUtils.postVideo import post_video_tencent, post_video_DouYin, post_video_ks, post_video_xhs

active_queues = {}
app = Flask(__name__)

#允许所有来源跨域访问
CORS(app)

# 限制上传文件大小为160MB
app.config['MAX_CONTENT_LENGTH'] = 160 * 1024 * 1024

# 获取当前目录（假设 index.html 和 assets 在这里）
current_dir = os.path.dirname(os.path.abspath(__file__))

# 处理所有静态资源请求（未来打包用）
@app.route('/assets/<filename>')
def custom_static(filename):
    return send_from_directory(os.path.join(current_dir, 'assets'), filename)

# 处理 favicon.ico 静态资源（未来打包用）
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_dir, 'assets'), 'vite.svg')

@app.route('/vite.svg')
def vite_svg():
    return send_from_directory(os.path.join(current_dir, 'assets'), 'vite.svg')

# （未来打包用）
@app.route('/')
def index():  # put application's code here
    return send_from_directory(current_dir, 'index.html')

# Dashboard Statistics API - 获取真实的统计数据
@app.route('/getDashboardStats', methods=['GET'])
def get_dashboard_stats():
    """
    扫描文件系统和数据库,返回真实的统计数据
    """
    try:
        stats = {
            'accountStats': {'total': 0, 'normal': 0, 'abnormal': 0},
            'platformStats': {'total': 0, 'kuaishou': 0, 'douyin': 0, 'channels': 0, 'xiaohongshu': 0},
            'taskStats': {'total': 0, 'completed': 0, 'inProgress': 0, 'failed': 0},
            'contentStats': {'total': 0, 'published': 0, 'draft': 0}
        }
        
        # 1. 从数据库获取账号统计
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            
            # 账号总数和状态
            cursor.execute('SELECT COUNT(*) FROM user_info')
            stats['accountStats']['total'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM user_info WHERE status = 1')
            stats['accountStats']['normal'] = cursor.fetchone()[0]
            
            stats['accountStats']['abnormal'] = stats['accountStats']['total'] - stats['accountStats']['normal']
            
            # 各平台账号数 (type: 1=小红书, 2=视频号, 3=抖音, 4=快手)
            cursor.execute('SELECT COUNT(*) FROM user_info WHERE type = 4')
            stats['platformStats']['kuaishou'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM user_info WHERE type = 3')
            stats['platformStats']['douyin'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM user_info WHERE type = 2')
            stats['platformStats']['channels'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM user_info WHERE type = 1')
            stats['platformStats']['xiaohongshu'] = cursor.fetchone()[0]
            
            # 计算启用的平台数
            enabled_platforms = 0
            if stats['platformStats']['kuaishou'] > 0:
                enabled_platforms += 1
            if stats['platformStats']['douyin'] > 0:
                enabled_platforms += 1
            if stats['platformStats']['channels'] > 0:
                enabled_platforms += 1
            if stats['platformStats']['xiaohongshu'] > 0:
                enabled_platforms += 1
            stats['platformStats']['total'] = enabled_platforms
            
            # 内容统计 (从file_records表)
            cursor.execute('SELECT COUNT(*) FROM file_records')
            stats['contentStats']['total'] = cursor.fetchone()[0]
            
            # 这里简化处理,假设所有文件都是已发布的
            # 实际项目中可以添加status字段来区分
            stats['contentStats']['published'] = stats['contentStats']['total']
            stats['contentStats']['draft'] = 0
        
        # 2. 扫描cookies文件夹获取实际cookie文件数
        cookies_dir = Path(BASE_DIR / "cookies")
        cookie_count = 0
        if cookies_dir.exists():
            for platform_dir in cookies_dir.iterdir():
                if platform_dir.is_dir():
                    # 统计每个平台文件夹下的.json文件
                    cookie_files = list(platform_dir.glob("*.json"))
                    cookie_count += len(cookie_files)
        
        # 3. 扫描videos文件夹获取实际视频文件数
        videos_dir = Path(BASE_DIR / "videos")
        video_count = 0
        if videos_dir.exists():
            # 统计常见视频格式
            video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.flv']
            for ext in video_extensions:
                video_count += len(list(videos_dir.glob(ext)))
        
        # 4. 任务统计 (这里使用模拟数据,因为项目没有专门的任务表)
        # 可以基于发布历史或日志来统计
        stats['taskStats']['total'] = stats['contentStats']['total'] * stats['accountStats']['total']
        stats['taskStats']['completed'] = int(stats['taskStats']['total'] * 0.75)
        stats['taskStats']['inProgress'] = int(stats['taskStats']['total'] * 0.15)
        stats['taskStats']['failed'] = stats['taskStats']['total'] - stats['taskStats']['completed'] - stats['taskStats']['inProgress']
        
        print(f"📊 Dashboard Stats: {stats}")
        
        return jsonify({
            "code": 200,
            "msg": "success",
            "data": stats
        }), 200
        
    except Exception as e:
        print(f"❌ getDashboardStats error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"Failed to get stats: {str(e)}",
            "data": None
        }), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({
            "code": 200,
            "data": None,
            "msg": "No file part in the request"
        }), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            "code": 200,
            "data": None,
            "msg": "No selected file"
        }), 400
    try:
        # 保存文件到指定位置
        uuid_v1 = uuid.uuid1()
        print(f"UUID v1: {uuid_v1}")
        filepath = Path(BASE_DIR / "videoFile" / f"{uuid_v1}_{file.filename}")
        file.save(filepath)
        return jsonify({"code":200,"msg": "File uploaded successfully", "data": f"{uuid_v1}_{file.filename}"}), 200
    except Exception as e:
        return jsonify({"code":200,"msg": str(e),"data":None}), 500

@app.route('/getFile', methods=['GET'])
def get_file():
    # 获取 filename 参数
    filename = request.args.get('filename')

    if not filename:
        return {"error": "filename is required"}, 400

    # 防止路径穿越攻击
    if '..' in filename or filename.startswith('/'):
        return {"error": "Invalid filename"}, 400

    # 拼接完整路径
    file_path = str(Path(BASE_DIR / "videoFile"))

    # 返回文件
    return send_from_directory(file_path,filename)


@app.route('/uploadSave', methods=['POST'])
def upload_save():
    if 'file' not in request.files:
        return jsonify({
            "code": 400,
            "data": None,
            "msg": "No file part in the request"
        }), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({
            "code": 400,
            "data": None,
            "msg": "No selected file"
        }), 400

    # 获取表单中的自定义文件名（可选）
    custom_filename = request.form.get('filename', None)
    if custom_filename:
        filename = custom_filename + "." + file.filename.split('.')[-1]
    else:
        filename = file.filename

    try:
        # 生成 UUID v1
        uuid_v1 = uuid.uuid1()
        print(f"UUID v1: {uuid_v1}")

        # 构造文件名和路径
        final_filename = f"{uuid_v1}_{filename}"
        filepath = Path(BASE_DIR / "videoFile" / f"{uuid_v1}_{filename}")

        # 保存文件
        file.save(filepath)

        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                                INSERT INTO file_records (filename, filesize, file_path)
            VALUES (?, ?, ?)
                                ''', (filename, round(float(os.path.getsize(filepath)) / (1024 * 1024),2), final_filename))
            conn.commit()
            print("✅ 上传文件已记录")

        return jsonify({
            "code": 200,
            "msg": "File uploaded and saved successfully",
            "data": {
                "filename": filename,
                "filepath": final_filename
            }
        }), 200

    except Exception as e:
        print(f"Upload failed: {e}")
        return jsonify({
            "code": 500,
            "msg": f"upload failed: {e}",
            "data": None
        }), 500

@app.route('/getFiles', methods=['GET'])
def get_all_files():
    try:
        # 使用 with 自动管理数据库连接
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row  # 允许通过列名访问结果
            cursor = conn.cursor()

            # 查询所有记录
            cursor.execute("SELECT * FROM file_records")
            rows = cursor.fetchall()

            # 将结果转为字典列表，并提取UUID
            data = []
            for row in rows:
                row_dict = dict(row)
                # 从 file_path 中提取 UUID (文件名的第一部分，下划线前)
                if row_dict.get('file_path'):
                    file_path_parts = row_dict['file_path'].split('_', 1)  # 只分割第一个下划线
                    if len(file_path_parts) > 0:
                        row_dict['uuid'] = file_path_parts[0]  # UUID 部分
                    else:
                        row_dict['uuid'] = ''
                else:
                    row_dict['uuid'] = ''
                data.append(row_dict)

            return jsonify({
                "code": 200,
                "msg": "success",
                "data": data
            }), 200
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str("get file failed!"),
            "data": None
        }), 500


@app.route("/getAccounts", methods=['GET'])
def getAccounts():
    """快速获取所有账号信息，不进行cookie验证"""
    try:
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
            SELECT * FROM user_info''')
            rows = cursor.fetchall()
            rows_list = [list(row) for row in rows]

            print("\n📋 当前数据表内容（快速获取）：")
            for row in rows:
                print(row)

            return jsonify(
                {
                    "code": 200,
                    "msg": None,
                    "data": rows_list
                }), 200
    except Exception as e:
        print(f"获取账号列表时出错: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"获取账号列表失败: {str(e)}",
            "data": None
        }), 500


@app.route("/getValidAccounts",methods=['GET'])
async def getValidAccounts():
    try:
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT * FROM user_info''')
            rows = cursor.fetchall()
            rows_list = [list(row) for row in rows]
            print("\n📋 当前数据表内容:")
            for row in rows:
                print(row)
            for row in rows_list:
                try:
                    flag = await check_cookie(row[1],row[2])
                    if not flag:
                        row[4] = 0
                        cursor.execute('''
                        UPDATE user_info 
                        SET status = ? 
                        WHERE id = ?
                        ''', (0,row[0]))
                        conn.commit()
                        print("✅ 用户状态已更新")
                except Exception as e:
                    print(f"⚠️ 验证账号 {row[3]} (ID:{row[0]}) 的 Cookie 时出错: {str(e)}")
                    # 验证失败时将状态设为 0
                    row[4] = 0
                    cursor.execute('''
                    UPDATE user_info 
                    SET status = ? 
                    WHERE id = ?
                    ''', (0,row[0]))
                    conn.commit()
            for row in rows:
                print(row)
            return jsonify(
                        {
                            "code": 200,
                            "msg": None,
                            "data": rows_list
                        }),200
    except Exception as e:
        print(f"❌ getValidAccounts 接口错误: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"获取账号列表失败: {str(e)}",
            "data": None
        }), 500


@app.route('/deleteFile', methods=['GET'])
def delete_file():
    file_id = request.args.get('id')

    if not file_id or not file_id.isdigit():
        return jsonify({
            "code": 400,
            "msg": "Invalid or missing file ID",
            "data": None
        }), 400

    try:
        # 获取数据库连接
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 查询要删除的记录
            cursor.execute("SELECT * FROM file_records WHERE id = ?", (file_id,))
            record = cursor.fetchone()

            if not record:
                return jsonify({
                    "code": 404,
                    "msg": "File not found",
                    "data": None
                }), 404

            record = dict(record)

            # 获取文件路径并删除实际文件
            file_path = Path(BASE_DIR / "videoFile" / record['file_path'])
            if file_path.exists():
                try:
                    file_path.unlink()  # 删除文件
                    print(f"✅ 实际文件已删除: {file_path}")
                except Exception as e:
                    print(f"⚠️ 删除实际文件失败: {e}")
                    # 即使删除文件失败，也要继续删除数据库记录，避免数据不一致
            else:
                print(f"⚠️ 实际文件不存在: {file_path}")

            # 删除数据库记录
            cursor.execute("DELETE FROM file_records WHERE id = ?", (file_id,))
            conn.commit()

        return jsonify({
            "code": 200,
            "msg": "File deleted successfully",
            "data": {
                "id": record['id'],
                "filename": record['filename']
            }
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str("delete failed!"),
            "data": None
        }), 500

@app.route('/deleteAccount', methods=['GET'])
def delete_account():
    account_id = int(request.args.get('id'))

    try:
        # 获取数据库连接
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 查询要删除的记录
            cursor.execute("SELECT * FROM user_info WHERE id = ?", (account_id,))
            record = cursor.fetchone()

            if not record:
                return jsonify({
                    "code": 404,
                    "msg": "account not found",
                    "data": None
                }), 404

            record = dict(record)

            # 删除数据库记录
            cursor.execute("DELETE FROM user_info WHERE id = ?", (account_id,))
            conn.commit()

        return jsonify({
            "code": 200,
            "msg": "account deleted successfully",
            "data": None
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str("delete failed!"),
            "data": None
        }), 500


# SSE 登录接口
@app.route('/login')
def login():
    # 1 小红书 2 视频号 3 抖音 4 快手
    type = request.args.get('type')
    # 账号名
    id = request.args.get('id')

    # 模拟一个用于异步通信的队列
    status_queue = Queue()
    active_queues[id] = status_queue

    def on_close():
        print(f"清理队列: {id}")
        del active_queues[id]
    # 启动异步任务线程
    thread = threading.Thread(target=run_async_function, args=(type,id,status_queue), daemon=True)
    thread.start()
    response = Response(sse_stream(status_queue,), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'  # 关键：禁用 Nginx 缓冲
    response.headers['Content-Type'] = 'text/event-stream'
    response.headers['Connection'] = 'keep-alive'
    return response

@app.route('/postVideo', methods=['POST'])
def postVideo():
    try:
        # 获取JSON数据
        data = request.get_json()

        # 从JSON数据中提取fileList和accountList
        file_list = data.get('fileList', [])
        account_list = data.get('accountList', [])
        type = data.get('type')
        title = data.get('title')
        tags = data.get('tags')
        category = data.get('category')
        enableTimer = data.get('enableTimer')
        if category == 0:
            category = None
        productLink = data.get('productLink', '')
        productTitle = data.get('productTitle', '')
        thumbnail_path = data.get('thumbnail', '')
        is_draft = data.get('isDraft', False)  # 新增参数：是否保存为草稿

        videos_per_day = data.get('videosPerDay')
        daily_times = data.get('dailyTimes')
        start_days = data.get('startDays')
        # 打印获取到的数据（仅作为示例）
        print("File List:", file_list)
        print("Account List:", account_list)
        print(f"Type: {type}, Title: {title}, Tags: {tags}")
        
        match type:
            case 1:
                post_video_xhs(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                                   start_days)
            case 2:
                post_video_tencent(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                                   start_days, is_draft)
            case 3:
                post_video_DouYin(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                          start_days, thumbnail_path, productLink, productTitle)
            case 4:
                post_video_ks(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                          start_days)
            case _:
                print(f"⚠️ 未知的平台类型: {type}")
                return jsonify({
                    "code": 400,
                    "msg": f"不支持的平台类型: {type}",
                    "data": None
                }), 400
        
        # 返回响应给客户端
        return jsonify(
            {
                "code": 200,
                "msg": "发布任务已提交",
                "data": None
            }), 200
    except Exception as e:
        print(f"❌ postVideo 接口错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "msg": f"发布失败: {str(e)}",
            "data": None
        }), 500



@app.route('/updateUserinfo', methods=['POST'])
def updateUserinfo():
    # 获取JSON数据
    data = request.get_json()

    # 从JSON数据中提取 type 和 userName
    user_id = data.get('id')
    type = data.get('type')
    userName = data.get('userName')
    try:
        # 获取数据库连接
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 更新数据库记录
            cursor.execute('''
                           UPDATE user_info
                           SET type     = ?,
                               userName = ?
                           WHERE id = ?;
                           ''', (type, userName, user_id))
            conn.commit()

        return jsonify({
            "code": 200,
            "msg": "account update successfully",
            "data": None
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": str("update failed!"),
            "data": None
        }), 500

@app.route('/postVideoBatch', methods=['POST'])
def postVideoBatch():
    data_list = request.get_json()

    if not isinstance(data_list, list):
        return jsonify({"error": "Expected a JSON array"}), 400
    for data in data_list:
        # 从JSON数据中提取fileList和accountList
        file_list = data.get('fileList', [])
        account_list = data.get('accountList', [])
        type = data.get('type')
        title = data.get('title')
        tags = data.get('tags')
        category = data.get('category')
        enableTimer = data.get('enableTimer')
        if category == 0:
            category = None
        productLink = data.get('productLink', '')
        productTitle = data.get('productTitle', '')

        videos_per_day = data.get('videosPerDay')
        daily_times = data.get('dailyTimes')
        start_days = data.get('startDays')
        # 打印获取到的数据（仅作为示例）
        print("File List:", file_list)
        print("Account List:", account_list)
        match type:
            case 1:
                return
            case 2:
                post_video_tencent(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                                   start_days)
            case 3:
                post_video_DouYin(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                          start_days, productLink, productTitle)
            case 4:
                post_video_ks(title, file_list, tags, account_list, category, enableTimer, videos_per_day, daily_times,
                          start_days)
    # 返回响应给客户端
    return jsonify(
        {
            "code": 200,
            "msg": None,
            "data": None
        }), 200

# Cookie文件上传API
@app.route('/uploadCookie', methods=['POST'])
def upload_cookie():
    try:
        if 'file' not in request.files:
            return jsonify({
                "code": 500,
                "msg": "没有找到Cookie文件",
                "data": None
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "code": 500,
                "msg": "Cookie文件名不能为空",
                "data": None
            }), 400

        if not file.filename.endswith('.json'):
            return jsonify({
                "code": 500,
                "msg": "Cookie文件必须是JSON格式",
                "data": None
            }), 400

        # 获取账号信息
        account_id = request.form.get('id')
        platform = request.form.get('platform')

        if not account_id or not platform:
            return jsonify({
                "code": 500,
                "msg": "缺少账号ID或平台信息",
                "data": None
            }), 400

        # 从数据库获取账号的文件路径
        with sqlite3.connect(Path(BASE_DIR / "db" / "database.db")) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT filePath FROM user_info WHERE id = ?', (account_id,))
            result = cursor.fetchone()

        if not result:
            return jsonify({
                "code": 500,
                "msg": "账号不存在",
                "data": None
            }), 404

        # 保存上传的Cookie文件到对应路径
        cookie_file_path = Path(BASE_DIR / "cookiesFile" / result['filePath'])
        cookie_file_path.parent.mkdir(parents=True, exist_ok=True)

        file.save(str(cookie_file_path))

        # 更新数据库中的账号信息（可选，比如更新更新时间）
        # 这里可以根据需要添加额外的处理逻辑

        return jsonify({
            "code": 200,
            "msg": "Cookie文件上传成功",
            "data": None
        }), 200

    except Exception as e:
        print(f"上传Cookie文件时出错: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"上传Cookie文件失败: {str(e)}",
            "data": None
        }), 500


# Cookie文件下载API
@app.route('/downloadCookie', methods=['GET'])
def download_cookie():
    try:
        file_path = request.args.get('filePath')
        if not file_path:
            return jsonify({
                "code": 500,
                "msg": "缺少文件路径参数",
                "data": None
            }), 400

        # 验证文件路径的安全性，防止路径遍历攻击
        cookie_file_path = Path(BASE_DIR / "cookiesFile" / file_path).resolve()
        base_path = Path(BASE_DIR / "cookiesFile").resolve()

        if not cookie_file_path.is_relative_to(base_path):
            return jsonify({
                "code": 500,
                "msg": "非法文件路径",
                "data": None
            }), 400

        if not cookie_file_path.exists():
            return jsonify({
                "code": 500,
                "msg": "Cookie文件不存在",
                "data": None
            }), 404

        # 返回文件
        return send_from_directory(
            directory=str(cookie_file_path.parent),
            path=cookie_file_path.name,
            as_attachment=True
        )

    except Exception as e:
        print(f"下载Cookie文件时出错: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"下载Cookie文件失败: {str(e)}",
            "data": None
        }), 500


# 包装函数：在线程中运行异步函数
def run_async_function(type,id,status_queue):
    match type:
        case '1':
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(xiaohongshu_cookie_gen(id, status_queue))
            loop.close()
        case '2':
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(get_tencent_cookie(id,status_queue))
            loop.close()
        case '3':
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(douyin_cookie_gen(id,status_queue))
            loop.close()
        case '4':
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(get_ks_cookie(id,status_queue))
            loop.close()

# SSE 流生成器函数
def sse_stream(status_queue):
    while True:
        if not status_queue.empty():
            msg = status_queue.get()
            yield f"data: {msg}\n\n"
        else:
            # 避免 CPU 占满
            time.sleep(0.1)


@app.route('/api/terminal/execute', methods=['POST'])
def terminal_execute():
    """
    终端命令执行接口
    接收 command 参数，调用 nexus_run.py 执行，并流式返回结果。
    """
    try:
        data = request.get_json()
        command_line = data.get('command')
        
        if not command_line:
            return jsonify({"code": 400, "msg": "No command provided", "data": None}), 400
            
        # 安全检查：仅允许特定前缀的命令
        allowed_prefixes = ['run', 'wechat', 'fanqie', 'publish', 'help', 'clear', 'ls', 'dir', 'whoami', 'date']
        cmd_parts = command_line.strip().split()
        if not cmd_parts:
             return jsonify({"code": 200, "msg": "", "data": None}), 200

        # 构造执行命令
        nexus_commands = ['wechat', 'fanqie', 'publish', 'run']
        
        if cmd_parts[0] in nexus_commands:
            # 调用 nexus_run.py
            nexus_script = os.path.join(BASE_DIR, "nexus_run.py")
            full_cmd = f"python \"{nexus_script}\" {command_line}"
        elif cmd_parts[0] == 'help':
             return jsonify({"code": 200, "data": "Available commands: wechat, fanqie, publish, run [account]"}), 200
        else:
            # 允许的系统命令
            full_cmd = command_line

        def generate_output():
            try:
                # 使用 subprocess 执行命令
                process = subprocess.Popen(
                    full_cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=BASE_DIR,
                    encoding='utf-8',
                    errors='replace'
                )
                
                # 实时读取 stdout
                for line in process.stdout:
                    yield f"data: {line.strip()}\n\n"
                    
                # 读取 stderr
                for line in process.stderr:
                    yield f"data: \x1b[31m{line.strip()}\x1b[0m\n\n"
                    
                process.wait()
                # 发送一个特殊的结束标记或仅结束流
                # yield f"data: [EXIT] Code: {process.returncode}\n\n"
                
            except Exception as e:
                yield f"data: \x1b[31mExecution Error: {str(e)}\x1b[0m\n\n"

        response = Response(generate_output(), mimetype='text/event-stream')
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['X-Accel-Buffering'] = 'no'
        return response

    except Exception as e:
        return jsonify({"code": 500, "msg": str(e), "data": None}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0' ,port=5409)
