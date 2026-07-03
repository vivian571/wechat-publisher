# 导入所需的库
import os           # 用于操作系统相关功能，如文件路径操作和目录创建
import re           # 用于正则表达式操作，例如清理文件名
import time         # 用于添加延迟
import random       # 用于生成随机延迟时间
import requests     # 用于发送 HTTP 请求
import logging      # 用于记录程序运行信息和错误
# 使用 parsel 进行数据解析，它支持 CSS Selector 和 XPath
from parsel import Selector
from datetime import datetime # 用于生成带时间戳的目录名
from typing import List, Optional, Tuple # 用于类型提示，增强代码可读性

# --- 配置日志记录 ---
# 设置日志记录的基本配置，将日志输出到控制台
# level=logging.INFO 表示记录 INFO 级别及以上的日志 (INFO, WARNING, ERROR, CRITICAL)
# format 指定了日志输出的格式，包括时间戳、日志级别和消息内容
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# --- 常量和配置 ---
# 请求头，模拟浏览器访问，提高成功率
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://fanqienovel.com/', # 增加 Referer 字段，模拟从主页跳转
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive', # 保持连接
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
}

# 基础 URL
BASE_URL = "https://fanqienovel.com"
# 请求超时时间 (秒)
REQUEST_TIMEOUT = 20
# 请求失败后的最大重试次数
MAX_RETRIES = 5 # 增加重试次数，提高鲁棒性
# 每次重试之间的基础延迟时间 (秒)
RETRY_DELAY = 5 # 增加重试延迟
# 获取章节列表时的随机延迟范围 (秒)
GET_LINKS_DELAY_RANGE = (1.5, 3.0) # 增加延迟范围
# 下载章节时的随机延迟范围 (秒)
DOWNLOAD_DELAY_RANGE = (1.0, 2.5) # 增加延迟范围

# 单个章节文件大小上限 (MB)
MAX_FILE_SIZE_MB = 20
# 将 MB 转换为字节
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# 番茄小说特有的字体映射数据 (用于解码混淆的文字)
# 这是从你的代码片段中提取的，用于将特定的字符编码映射回实际的文字或数字
FONT_DECODE_MAP = {
    '58670': '0', '58413': '1', '58678': '2', '58371': '3', '58353': '4', '58480': '5',
    '58359': '6', '58449': '7', '58540': '8', '58692': '9', '58712': 'a', '58542': 'b',
    '58575': 'c', '58626': 'd', '58691': 'e', '58561': 'f', '58362': 'g', '58619': 'h',
    '58430': 'i', '58531': 'j', '58588': 'k', '58440': 'l', '58681': 'm', '58631': 'n',
    '58376': 'o', '58429': 'p', '58555': 'q', '58498': 'r', '58518': 's', '58453': 't',
    '58397': 'u', '58356': 'v', '58435': 'w', '58514': 'x', '58482': 'y', '58529': 'z',
    '58515': 'A', '58688': 'B', '58709': 'C', '58344': 'D', '58656': 'E', '58381': 'F',
    '58576': 'G', '58516': 'H', '58463': 'I', '58649': 'J', '58571': 'K', '58558': 'L',
    '58433': 'M', '58517': 'N', '58387': 'O', '58687': 'P', '58537': 'Q', '58541': 'R',
    '58458': 'S', '58390': 'T', '58466': 'U', '58386': 'V', '58697': 'W', '58519': 'X',
    '58511': 'Y', '58634': 'Z', '58611': '的', '58590': '一', '58398': '是', '58422': '了',
    '58657': '我', '58666': '不', '58562': '人', '58345': '在', '58510': '他', '58496': '有',
    '58654': '这', '58441': '个', '58493': '上', '58714': '们', '58618': '来', '58528': '到',
    '58403': '大', '58461': '地', '58481': '为', '58700': '子', '58708': '中', '58503': '你',
    '58442': '说', '58639': '生', '58506': '国', '58663': '年', '58436': '着', '58563': '就',
    '58391': '那', '58357': '和', '58354': '要', '58695': '她', '58372': '出', '58696': '也',
    '58551': '得', '58445': '里', '58408': '后', '58599': '自', '58424': '以', '58394': '会',
    '58348': '家', '58426': '可', '58673': '下', '58417': '而', '58556': '过', '58603': '天',
    '58565': '去', '58604': '能', '58522': '对', '58632': '小', '58622': '多', '58350': '然',
    '58605': '于', '58617': '心', '58401': '学', '58637': '么', '58684': '之', '58382': '都',
    '58464': '好', '58487': '看', '58693': '起', '58608': '发', '58392': '当', '58474': '没',
    '58601': '成', '58355': '只', '58573': '如', '58499': '事', '58469': '把', '58361': '还',
    '58698': '用', '58489': '第', '58711': '样', '58457': '道', '58635': '想', '58492': '作',
    '58647': '种', '58623': '开', '58521': '美', '58609': '总', '58530': '从', '58665': '无',
    '58652': '情', '58676': '己', '58456': '面', '58581': '最', '58509': '女', '58488': '但',
    '58363': '现', '58685': '前', '58396': '些', '58523': '所', '58471': '同', '58485': '日',
    '58613': '手', '58533': '又', '58589': '行', '58527': '意', '58593': '动', '58699': '方',
    '58707': '期', '58414': '它', '58596': '头', '58570': '经', '58660': '长', '58364': '儿',
    '58526': '回', '58501': '位', '58638': '分', '58404': '爱', '58677': '老', '58535': '因',
    '58629': '很', '58577': '绘', '58606': '多', '58497': '法', '58662': '间', '58479': '斯',
    '58532': '知', '58380': '世', '58385': '什', '58405': '两', '58644': '次', '58578': '使',
    '58505': '身', '58564': '者', '58412': '被', '58686': '高', '58624': '已', '58667': '亲',
    '58607': '其', '58616': '进', '58368': '此', '58427': '话', '58423': '常', '58633': '与',
    '58525': '活', '58543': '正', '58418': '感', '58597': '见', '58683': '明', '58507': '问',
    '58621': '力', '58703': '理', '58438': '尔', '58536': '占', '58384': '文', '58484': '几',
    '58539': '定', '58554': '木', '58421': '公', '58347': '特', '58569': '做', '58710': '外',
    '58574': '孩', '58375': '相', '58645': '西', '58592': '果', '58572': '走', '58388': '将',
    '58370': '月', '58399': '十', '58651': '实', '58546': '向', '58504': '声', '58419': '车',
    '58407': '全', '58672': '信', '58675': '重', '58538': '三', '58465': '机', '58374': '工',
    '58579': '物', '58402': '气', '58702': '每', '58553': '并', '58360': '别', '58389': '真',
    '58560': '打', '58690': '太', '58473': '新', '58512': '比', '58653': '才', '58704': '便',
    '58545': '夫', '58641': '再', '58475': '书', '58583': '部', '58472': '水', '58478': '像',
    '58664': '眼', '58586': '等', '58568': '体', '58674': '却', '58490': '加', '58476': '电',
    '58346': '主', '58630': '界', '58595': '门', '58502': '利', '58713': '海', '58587': '受',
    '58548': '听', '58351': '表', '58547': '德', '58443': '少', '58460': '克', '58636': '代',
    '58585': '员', '58625': '许', '58694': '稜', '58428': '先', '58640': '口', '58628': '由',
    '58612': '死', '58446': '安', '58468': '写', '58410': '性', '58508': '马', '58594': '光',
    '58483': '白', '58544': '或', '58495': '住', '58450': '难', '58643': '望', '58486': '教',
    '58406': '命', '58447': '花', '58669': '结', '58415': '乐', '58444': '色', '58549': '更',
    '58494': '拉', '58409': '东', '58658': '神', '58557': '记', '58602': '处', '58559': '让',
    '58610': '母', '58513': '父', '58500': '应', '58378': '直', '58680': '字', '58352': '场',
    '58383': '平', '58454': '报', '58671': '友', '58668': '关', '58452': '放', '58627': '至',
    '58400': '张', '58455': '认', '58416': '接', '58552': '告', '58614': '入', '58582': '笑',
    '58534': '内', '58701': '英', '58349': '军', '58491': '候', '58467': '民', '58365': '岁',
    '58598': '往', '58425': '何', '58462': '度', '58420': '山', '58661': '觉', '58615': '路',
    '58648': '带', '58470': '万', '58377': '男', '58520': '边', '58646': '风', '58600': '解',
    '58431': '叫', '58715': '任', '58524': '金', '58439': '快', '58566': '原', '58477': '吃',
    '58642': '妈', '58437': '变', '58411': '通', '58451': '师', '58395': '立', '58369': '象',
    '58706': '数', '58705': '四', '58379': '失', '58567': '满', '58373': '战', '58448': '远',
    '58659': '格', '58434': '士', '58679': '音', '58432': '轻', '58689': '目', '58591': '条',
    '58682': '呢',
}


# --- 辅助函数 ---

def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除或替换不适用于文件名的字符。
    Args:
        filename (str): 原始文件名 (通常是章节标题)。
    Returns:
        str: 清理后的安全文件名。
    """
    # 移除或替换 Windows 和 Linux/macOS 中不允许的字符
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
    # 移除字符串开头和结尾的空白字符
    sanitized = sanitized.strip()
    # 防止文件名过长 (可选，但推荐)
    max_len = 150 # 可以根据需要调整
    if len(sanitized) > max_len:
        sanitized = sanitized[:max_len].rstrip('_') # 截断并移除末尾可能的下划线
    # 确保文件名不为空
    if not sanitized:
        sanitized = f"未知章节_{random.randint(1000, 9999)}" # 提供一个随机的默认名
    return sanitized

def make_request(session: requests.Session, url: str, retries: int = MAX_RETRIES, delay_range: Tuple[float, float] = (1.0, 2.0)) -> Optional[requests.Response]:
    """
    发送 GET 请求，包含重试逻辑和随机延迟。
    Args:
        session (requests.Session): requests 会话对象。
        url (str): 请求的目标 URL。
        retries (int): 最大重试次数。
        delay_range (Tuple[float, float]): 每次请求前的随机延迟范围 (秒)。
    Returns:
        Optional[requests.Response]: 成功则返回 Response 对象，否则返回 None。
    """
    for attempt in range(retries):
        try:
            # 添加随机延迟，模拟用户行为，减轻服务器压力
            delay = random.uniform(delay_range[0], delay_range[1])
            logging.debug(f"等待 {delay:.2f} 秒...") # 调试信息，显示每次请求前的延迟
            time.sleep(delay)

            # 发送 GET 请求
            response = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status() # 检查 HTTP 错误状态码 (4xx 或 5xx)，如果发生错误会抛出异常

            # 尝试根据 Content-Type 或启发式方法确定编码，优先使用 'utf-8'
            response.encoding = response.apparent_encoding if response.apparent_encoding else 'utf-8'
            if 'charset=' not in response.headers.get('content-type', '').lower():
                 response.encoding = 'utf-8' # 如果响应头没有指定编码，强制使用 utf-8

            logging.info(f"请求成功: {url} (尝试 {attempt + 1}/{retries})")
            return response

        except requests.exceptions.Timeout:
            logging.warning(f"请求超时: {url} (尝试 {attempt + 1}/{retries})")
        except requests.exceptions.ConnectionError as e:
             logging.warning(f"连接错误: {url} (尝试 {attempt + 1}/{retries}) - 错误: {e}")
        except requests.exceptions.HTTPError as e:
             logging.warning(f"HTTP 错误: {url} (尝试 {attempt + 1}/{retries}) - 状态码: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.warning(f"请求失败: {url} (尝试 {attempt + 1}/{retries}) - 错误: {e}")
        except Exception as e:
             logging.warning(f"请求过程中发生未知错误: {url} (尝试 {attempt + 1}/{retries}) - 错误: {e}")

        if attempt < retries - 1:
            # 指数退避 + 随机抖动 的延迟策略
            # 延迟时间随尝试次数增加，并加上随机抖动，避免请求过于同步
            wait_time = RETRY_DELAY * (2 ** attempt) + random.uniform(0, RETRY_DELAY)
            logging.info(f"等待 {wait_time:.2f} 秒后重试...")
            time.sleep(wait_time)
        else:
            logging.error(f"请求失败: {url} - 已达到最大重试次数，放弃。")
            return None
    return None # 所有重试均失败

def decode_fanqie_content(encoded_text: str, decode_map: dict) -> str:
    """
    根据番茄小说的字体映射字典解码混淆的文本。
    Args:
        encoded_text (str): 从网页中提取的包含混淆字符的文本。
        decode_map (dict): 字体编码到实际字符的映射字典。
    Returns:
        str: 解码后的原始文本。
    """
    decoded_content = ""
    for char in encoded_text:
        # 获取字符的 Unicode 序数 (整数)
        char_ord = str(ord(char))
        # 在映射字典中查找序数对应的实际字符
        # 如果找到，使用实际字符；如果没找到 (即不是混淆字符)，使用原始字符
        decoded_char = decode_map.get(char_ord, char)
        decoded_content += decoded_char
    return decoded_content


# --- 主要功能函数 ---

def get_book_info_and_chapters(session: requests.Session, book_url: str) -> Tuple[Optional[str], List[Tuple[str, str]]]:
    """
    获取小说书名和所有章节的链接及标题列表。
    Args:
        session (requests.Session): requests 会话对象。
        book_url (str): 小说的主页 URL (目录页)。
    Returns:
        Tuple[Optional[str], List[Tuple[str, str]]]: 返回书名 (str 或 None) 和一个包含 (章节标题, 章节URL) 元组的列表。
    Raises:
        Exception: 如果多次尝试后仍无法获取章节列表。
    """
    logging.info(f"开始获取书籍信息和章节列表: {book_url}")
    response = make_request(session, book_url, retries=MAX_RETRIES, delay_range=GET_LINKS_DELAY_RANGE)

    if not response:
        raise Exception(f"无法访问书籍主页或获取内容: {book_url}")

    try:
        selector = Selector(text=response.text) # 使用 Parsel 解析 HTML

        # --- 提取书名 ---
        # 定义可能的书名 CSS 选择器列表，按优先级排序
        book_title_selectors = [
            '.info-name h1::text', # 来自你的代码片段
            '.book-title h1::text',
            'h1.book-name::text',
            'title::text', # 备用，提取页面标题
        ]
        book_name = None
        for selector_str in book_title_selectors:
            book_name = selector.css(selector_str).get()
            if book_name:
                book_name = book_name.strip()
                # 如果是从页面标题提取，可能需要进一步清理，例如移除网站名
                if ' - 番茄小说' in book_name:
                     book_name = book_name.split(' - 番茄小说')[0].strip()
                logging.info(f"使用选择器 '{selector_str}' 找到书名: {book_name}")
                break
        if not book_name:
             book_name = "未知书籍"
             logging.warning(f"无法找到书籍标题，使用默认名称: {book_name}")


        # --- 提取章节链接和标题 ---
        # 定义可能的章节列表项的选择器列表，按优先级排序
        # 我们需要同时获取章节标题和链接 (href属性)
        chapter_item_selectors = [
             '.chapter-item a[href^="/reader/"]', # 精确匹配 /reader/ 开头的 a 标签
             '.chapter-item-title', # 来自你的代码片段，需要同时获取其文本和父元素a的href
             '.catalog-list a[href^="/reader/"]',
             'a[href*="/reader/"]', # 匹配任何包含 /reader/ 的链接作为后备
        ]

        chapter_items = []
        for selector_str in chapter_item_selectors:
             # 注意：有些选择器直接定位到 a 标签，有些定位到标题元素
             # 如果定位到标题元素，我们需要找到其父级 a 标签来获取链接
             elements = selector.css(selector_str).getall() # getall() 返回匹配到的所有元素的HTML字符串或文本
             if elements:
                 # 如果选择器直接是 a 标签
                 if selector_str.endswith('a[href^="/reader/"]') or selector_str.endswith('a[href*="/reader/"]'):
                      chapter_items = selector.css(selector_str) # 获取 Parsel Selector Elements
                      logging.info(f"使用选择器 '{selector_str}' 找到 {len(chapter_items)} 个章节链接元素 (直接a标签)。")
                      break # 找到后即停止尝试其他选择器
                 # 如果选择器定位到标题元素，需要找到父级 a
                 elif selector_str == '.chapter-item-title': # 针对你提供的 .chapter-item-title
                      # 找到 .chapter-item-title 元素，然后找其父级 a 标签
                      chapter_items = selector.css(selector_str).xpath('parent::a') # 使用 XPath 查找父级 a
                      if not chapter_items:
                           # 尝试获取 .chapter-item-title 本身，然后从它的 class 向上找 a
                           # 这种方式更复杂，如果上面的 xpath('parent::a') 不行，可能需要更复杂的逻辑
                           logging.warning(f"使用选择器 '{selector_str}' 找到元素，但无法通过 XPath 找到父级 a 标签。")
                           continue # 尝试下一个选择器
                      logging.info(f"使用选择器 '{selector_str}' 找到 {len(chapter_items)} 个章节链接元素 (通过标题元素查找父级a)。")
                      break

        if not chapter_items:
             logging.error("在页面上找不到任何章节链接元素，请检查网站结构是否已更改或选择器是否正确。")
             raise Exception("无法解析章节列表。")

        # 提取章节标题和构建完整的章节 URL
        chapter_list_data = []
        for item in chapter_items:
            href = item.css('::attr(href)').get() # 获取链接
            title = item.css('::text').get() or item.xpath('string()').get() # 获取标题文本，如果::text失败则获取所有文本
            if href and title:
                full_url = BASE_URL + href if href.startswith('/') else href # 构建完整URL
                chapter_list_data.append((title.strip(), full_url)) # 保存 (标题, URL) 元组

        if not chapter_list_data:
             logging.warning("虽然找到了链接元素，但未能提取到有效的章节 URL 或标题。")
             raise Exception("未能提取有效的章节链接或标题。")

        logging.info(f"成功获取到 {len(chapter_list_data)} 个章节 (标题, 链接) 对。")
        return book_name, chapter_list_data

    except Exception as e:
        logging.error(f"解析书籍信息或章节列表时出错: {e}")
        raise Exception(f"解析书籍信息或章节列表失败: {e}")


def download_chapter(session: requests.Session, chapter_title: str, chapter_url: str, save_path: str, decode_map: dict, max_size_bytes: int) -> bool:
    """
    下载单个章节内容，解码，检查大小，并保存为 txt 文件。
    Args:
        session (requests.Session): requests 会话对象。
        chapter_title (str): 章节的标题。
        chapter_url (str): 章节的 URL。
        save_path (str): 章节文件保存的目录路径。
        decode_map (dict): 字体解码映射字典。
        max_size_bytes (int): 单个文件最大允许的字节数。
    Returns:
        bool: 下载、解码、检查大小并保存成功返回 True，否则返回 False。
    """
    logging.info(f"--- 开始下载章节: {chapter_title} ---")
    logging.info(f"章节 URL: {chapter_url}")

    response = make_request(session, chapter_url, retries=MAX_RETRIES, delay_range=DOWNLOAD_DELAY_RANGE)

    if not response:
        logging.error(f"下载章节失败（多次重试后）: {chapter_title} - {chapter_url}")
        return False

    try:
        selector = Selector(text=response.text) # 使用 Parsel 解析 HTML

        # --- 提取章节内容 ---
        # 定义可能的内容容器 CSS 选择器列表
        # 优先尝试直接获取段落文本的选择器
        # 再尝试获取整个内容容器，然后提取其内的文本
        content_selectors = [
            '.muye-reader-content-16 p::text', # 来自你的代码片段，直接获取p标签的文本列表
            '.reader-content p::text',
            '.article-content p::text',
            '.chapter-content p::text',
            'div.text p::text',
            # 如果上述获取p标签文本失败，尝试获取整个容器元素并提取所有文本
            '.muye-reader-content-16',
            '.reader-content',
            '.article-content',
            '.chapter-content',
            '#content', # 通用ID
            '.content', # 通用类名
            'div.text',
        ]

        raw_content_parts = [] # 用于存放提取到的原始文本部分
        content_found = False

        for selector_str in content_selectors:
            # 尝试直接获取文本列表 (针对 p::text 选择器)
            if '::text' in selector_str:
                parts = selector.css(selector_str).getall()
                if parts:
                    raw_content_parts = parts
                    content_found = True
                    logging.debug(f"使用选择器 '{selector_str}' 找到内容文本部分 (列表)。")
                    break # 找到了，停止尝试其他选择器
            else: # 尝试获取内容容器元素 (针对非 ::text 选择器)
                container = selector.css(selector_str).first # first() 获取第一个匹配的元素
                if container:
                    # 使用 XPath string() 获取容器内所有文本，忽略HTML标签
                    full_text = container.xpath('string()').get()
                    if full_text:
                        raw_content_parts = [full_text] # 包装成列表以便后续处理
                        content_found = True
                        logging.debug(f"使用选择器 '{selector_str}' 找到内容容器并提取所有文本。")
                        break # 找到了，停止尝试其他选择器

        if not content_found or not raw_content_parts:
            logging.error(f"无法找到章节内容容器或提取内容，URL: {chapter_url}")
            return False

        # 将内容部分合并成一个字符串，处理段落换行
        # 如果是 p::text 提取的列表，用双换行符连接
        # 如果是 xpath('string()') 提取的单个字符串，它可能已经包含了换行符，但这里统一处理
        raw_content_text = '\n\n'.join(raw_content_parts).strip()

        # --- 解码混淆的文本 ---
        decoded_content = decode_fanqie_content(raw_content_text, decode_map)
        logging.debug(f"章节内容已解码 ({len(decoded_content)} 字符).")

        # --- 格式化最终章节文本 ---
        final_chapter_text = f"【{chapter_title}】\n\n{decoded_content}\n\n"

        # --- 清理和格式化文本 ---
        # 移除常见的广告、章节控制等无关文本行（基于常见经验）
        # 注意：这可能需要根据实际下载内容进行调整
        cleaned_lines = []
        # 分割成行进行处理，移除只包含空白或特定模式的行
        for line in final_chapter_text.splitlines():
             stripped_line = line.strip()
             # 过滤掉可能是广告、版权信息或分页符的行
             if not stripped_line or \
                "番茄小说" in stripped_line or \
                "版权所有" in stripped_line or \
                "继续阅读" in stripped_line or \
                "下一章" in stripped_line or \
                "上一章" in stripped_line or \
                re.fullmatch(r'第\s*\d+\s*页', stripped_line) or \
                re.fullmatch(r'-+\s*\d+\s*-+', stripped_line):
                 logging.debug(f"过滤掉可能的无关行: {stripped_line[:50]}...") # 记录过滤掉的行
                 continue
             cleaned_lines.append(line) # 保留原始行（包含缩进等）

        # 重新组合清理后的文本
        cleaned_chapter_text = '\n'.join(cleaned_lines).strip() + "\n\n" # 保证末尾有空行

        # --- 检查文件大小限制 ---
        # 将清理后的文本编码为 UTF-8 并计算字节数
        encoded_text_bytes = cleaned_chapter_text.encode('utf-8')
        file_size_bytes = len(encoded_text_bytes)

        if file_size_bytes > max_size_bytes:
            logging.warning(f"章节内容过大 ({file_size_bytes / 1024:.2f} KB)，超过 {max_size_bytes / 1024 / 1024:.2f} MB 限制，跳过保存: {chapter_title}")
            return False # 跳过保存此章节

        # --- 保存文件 ---
        safe_title = sanitize_filename(chapter_title)
        # 保存为单独的 txt 文件，文件名包含章节标题
        file_path = os.path.join(save_path, f"{safe_title}.txt")

        try:
            # 使用 'w' 模式写入，会覆盖同名文件（每个章节一个文件，不需要 'a'）
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_chapter_text) # 写入清理后的文本
            logging.info(f"成功下载并保存: {safe_title}.txt ({file_size_bytes / 1024:.2f} KB)")
            return True
        except IOError as e:
            logging.error(f"保存文件失败: {file_path} - 错误: {e}")
            return False
        except Exception as e:
             logging.error(f"写入文件时发生未知错误: {file_path} - 错误: {e}")
             return False

    except Exception as e:
        logging.error(f"解析章节内容或处理文件时出错: {chapter_url} - 错误: {e}")
        return False

# --- 主执行函数 ---
def main():
    """
    主函数，执行小说下载流程。
    """
    # 获取用户输入的小说主页链接
    import sys
    if len(sys.argv) > 1:
        book_url = sys.argv[1].strip()
        logging.info(f"从命令行接收到 URL: {book_url}")
    else:
        book_url = input(f"请输入番茄小说书籍主页链接 (例如: {BASE_URL}/page/...) : ").strip()

    # 验证输入链接的有效性
    if not book_url.startswith(BASE_URL + '/page/'):
        logging.error(f"错误：请输入正确的番茄小说书籍主页链接，应以 {BASE_URL}/page/ 开头")
        return # 输入无效，退出程序

    # 使用 requests.Session 管理会话，可以保持连接和cookies
    with requests.Session() as session:
        book_name = None
        chapter_links_data = []

        try:
            # 1. 获取书籍信息和所有章节链接及标题
            # get_book_info_and_chapters 函数现在返回书名和章节列表
            book_name, chapter_links_data = get_book_info_and_chapters(session, book_url)
            if not chapter_links_data:
                 logging.error("未能获取章节列表，无法继续下载。")
                 return # 没有章节列表，直接退出

            total_chapters = len(chapter_links_data)
            logging.info(f"共获取到 {total_chapters} 个章节。")

            # --- 创建保存目录 ---
            try:
                # 使用书名和时间戳创建目录名
                safe_book_name = sanitize_filename(book_name)
                save_dir = f"{safe_book_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.makedirs(save_dir, exist_ok=True) # exist_ok=True 允许目录已存在，不会报错
                logging.info(f"小说内容将保存至目录: {save_dir}")
            except Exception as e:
                logging.error(f"创建保存目录失败: {e}")
                return # 创建目录失败，无法继续

            # 2. 逐个下载章节
            downloaded_count = 0
            failed_chapters = []
            # 遍历章节列表数据 [(title, url), ...]
            for idx, (title, url) in enumerate(chapter_links_data, 1):
                # 调用 download_chapter 函数下载并保存单个章节
                # 传递字体映射字典和文件大小限制
                if download_chapter(session, title, url, save_dir, FONT_DECODE_MAP, MAX_FILE_SIZE_BYTES):
                    downloaded_count += 1
                else:
                    # download_chapter 内部会记录详细错误信息，这里只需记录失败的章节
                    failed_chapters.append((title, url)) # 记录失败的章节标题和 URL

            # 3. 下载完成总结
            logging.info("------ 下载任务完成 ------")
            logging.info(f"成功下载章节数: {downloaded_count}/{total_chapters}")
            if failed_chapters:
                logging.warning(f"失败章节数: {len(failed_chapters)}")
                logging.warning("失败的章节 (标题, 链接):")
                for failed_title, failed_url in failed_chapters:
                    logging.warning(f"- {failed_title}: {failed_url}")
            else:
                logging.info("所有章节均已成功下载！")
            logging.info(f"文件保存在目录: {save_dir}")

        except Exception as e:
            # 捕获在获取章节列表或下载循环中可能出现的未处理异常
            logging.critical(f"下载过程中发生严重错误: {e}") # 使用 critical 级别表示严重错误


# --- 程序入口 ---
# 确保脚本作为主程序运行时才执行 main() 函数
if __name__ == "__main__":
    main()