"""
测试 Dev.to 标签清理功能
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.devto_adapter import DevToAdapter

def test_tag_sanitization():
    """测试标签清理功能"""
    
    # 创建适配器实例 (使用测试 API Key)
    adapter = DevToAdapter("test_api_key")
    
    # 测试用例
    test_cases = [
        ("developer-tools", "developertools"),
        ("machine learning", "machinelearning"),
        ("web-dev", "webdev"),
        ("python_3.11", "python_311"),
        ("C++", "c"),
        ("Node.js", "nodejs"),
        ("front-end", "frontend"),
        ("back-end", "backend"),
        ("AI/ML", "aiml"),
        ("test", "test"),  # 无需清理
    ]
    
    print("=" * 60)
    print("Dev.to 标签清理测试")
    print("=" * 60)
    
    all_passed = True
    for input_tag, expected in test_cases:
        result = adapter._sanitize_tag(input_tag)
        passed = result == expected
        
        status = "✅" if passed else "❌"
        print(f"{status} '{input_tag}' -> '{result}' (期望: '{expected}')")
        
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("✅ 所有标签清理测试通过!")
    else:
        print("❌ 部分测试失败")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = test_tag_sanitization()
    sys.exit(0 if success else 1)
