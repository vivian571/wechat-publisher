import os
import shutil
import hashlib
from pathlib import Path
from typing import List, Optional, Union, Tuple, Dict, Any
import mimetypes


def ensure_directory_exists(directory: Union[str, Path]) -> Path:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory: 目录路径
        
    Returns:
        解析后的Path对象
    """
    path = Path(directory).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_checksum(file_path: Union[str, Path], algorithm: str = 'md5', 
                     chunk_size: int = 8192) -> str:
    """
    计算文件的校验和
    
    Args:
        file_path: 文件路径
        algorithm: 哈希算法，支持'md5', 'sha1', 'sha256'
        chunk_size: 读取块大小
        
    Returns:
        文件的十六进制哈希值
    """
    hash_func = getattr(hashlib, algorithm.lower(), hashlib.md5)()
    file_path = Path(file_path)
    
    with file_path.open('rb') as f:
        while chunk := f.read(chunk_size):
            hash_func.update(chunk)
            
    return hash_func.hexdigest()


def find_files(directory: Union[str, Path], 
              extensions: Optional[List[str]] = None,
              recursive: bool = True) -> List[Path]:
    """
    查找指定目录下的文件
    
    Args:
        directory: 要搜索的目录
        extensions: 文件扩展名列表（不包含点），如 ['jpg', 'png']
        recursive: 是否递归搜索子目录
        
    Returns:
        匹配的文件路径列表
    """
    directory = Path(directory)
    if not directory.is_dir():
        return []
        
    if extensions:
        extensions = {f'.{ext.lstrip(".").lower()}' for ext in extensions}
    
    files = []
    
    if recursive:
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                if not extensions or file_path.suffix.lower() in extensions:
                    files.append(file_path)
    else:
        for file_path in directory.iterdir():
            if file_path.is_file():
                if not extensions or file_path.suffix.lower() in extensions:
                    files.append(file_path)
    
    return sorted(files)


def read_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
    """
    读取文件内容
    
    Args:
        file_path: 文件路径
        encoding: 文件编码
        
    Returns:
        文件内容字符串
    """
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()


def write_file(file_path: Union[str, Path], content: str, 
              encoding: str = 'utf-8', mode: str = 'w') -> None:
    """
    写入文件内容
    
    Args:
        file_path: 文件路径
        content: 要写入的内容
        encoding: 文件编码
        mode: 写入模式，'w'为覆盖，'a'为追加
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, mode, encoding=encoding) as f:
        f.write(content)


def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    获取文件信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        包含文件信息的字典，包括大小、修改时间、创建时间等
    """
    file_path = Path(file_path)
    stat = file_path.stat()
    
    return {
        'path': str(file_path),
        'name': file_path.name,
        'size': stat.st_size,
        'size_human': _format_size(stat.st_size),
        'modified_time': stat.st_mtime,
        'created_time': stat.st_ctime,
        'is_file': file_path.is_file(),
        'is_dir': file_path.is_dir(),
        'suffix': file_path.suffix.lower(),
        'mime_type': mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    }


def _format_size(size: int) -> str:
    """将字节数格式化为易读的字符串"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def backup_file(file_path: Union[str, Path], backup_dir: Optional[Union[str, Path]] = None, 
               suffix: str = '.bak') -> Optional[Path]:
    """
    备份文件
    
    Args:
        file_path: 要备份的文件路径
        backup_dir: 备份目录，如果为None则备份到原目录
        suffix: 备份文件后缀
        
    Returns:
        备份文件的路径，如果备份失败则返回None
    """
    file_path = Path(file_path)
    if not file_path.exists() or not file_path.is_file():
        return None
        
    if backup_dir is None:
        backup_dir = file_path.parent
    else:
        backup_dir = Path(backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)
    
    backup_path = backup_dir / f"{file_path.name}{suffix}"
    
    # 如果备份文件已存在，则添加数字后缀
    counter = 1
    while backup_path.exists():
        backup_path = backup_dir / f"{file_path.name}.{counter}{suffix}"
        counter += 1
    
    try:
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e:
        return None

def move_file_to_published(file_path: Union[str, Path], watch_dir: Union[str, Path], published_dir: Union[str, Path]) -> Optional[Path]:
    """
    将文件移动到已发布目录，并保留子目录结构

    Args:
        file_path: 要移动的文件路径
        watch_dir: 监控的根目录
        published_dir: 已发布文章的根目录

    Returns:
        移动后文件的路径，如果移动失败则返回None
    """
    file_path = Path(file_path).resolve()
    watch_dir = Path(watch_dir).resolve()
    published_dir = Path(published_dir).resolve()

    try:
        # 获取相对路径
        relative_path = file_path.relative_to(watch_dir)
        
        # 构建目标路径
        destination_path = published_dir / relative_path
        
        # 创建目标目录
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 移动文件
        shutil.move(str(file_path), str(destination_path))
        
        return destination_path
    except Exception as e:
        # 在实际应用中，这里应该使用日志记录错误
        print(f"Error moving file {file_path}: {e}")
        return None
