import re
import sys

# 本地高危 Docker 基础组件 CVE 碰撞映射数据库，拒绝任何省略占位
CVE_DANGER_DATABASE = {
    "openssl:1.1.1": {"cve": "CVE-2023-38408", "name": "OpenSSL 远程代码执行高危漏洞", "severity": "CRITICAL"},
    "log4j:2.14": {"cve": "CVE-2021-44228", "name": "Apache Log4j2 远程代码执行核弹级漏洞", "severity": "CRITICAL"},
    "python:3.7": {"cve": "CVE-2022-45061", "name": "Python 基础库 CPU 拒绝服务漏洞", "severity": "HIGH"},
    "ubuntu:18.04": {"cve": "CVE-2023-2640", "name": "Ubuntu 内核本地权限提升高危漏洞", "severity": "HIGH"}
}

class DockerfileStaticParser:
    def __init__(self):
        # 高精捕获从基础镜像 FROM pkg:ver
        self.from_pattern = re.compile(r"^FROM\s+([\w\-\.]+):([\w\-\.]+)", re.IGNORECASE | re.MULTILINE)
        # 精准匹配所有 pkg=version 的系统软件包声明
        self.pkg_ver_pattern = re.compile(r"([\w\-\.]+)=([\w\-\.]+)", re.IGNORECASE)

    def extract_dependencies(self, dockerfile_content):
        """工作流一：静态分析 Dockerfile 文本，精准捕获基础镜像及虚拟层 apt 包版本"""
        dependencies = []
        
        # 1. 扫描提取 FROM 基础镜像底座
        from_matches = self.from_pattern.findall(dockerfile_content)
        for pkg, ver in from_matches:
            dependencies.append({"package": pkg.strip(), "version": ver.strip(), "type": "BASE_IMAGE"})
            
        # 2. 扫描提取所有系统依赖组件
        pkg_matches = self.pkg_ver_pattern.findall(dockerfile_content)
        for pkg, ver in pkg_matches:
            dependencies.append({"package": pkg.strip(), "version": ver.strip(), "type": "SYS_PACKAGE"})
                
        return dependencies


class SecurityCollisionBreaker:
    def __init__(self, target_severity_limit="CRITICAL"):
        self.limit = target_severity_limit

    def enforce_threat_check(self, extracted_deps):
        """工作流二：碰撞本地漏洞数据库，一旦发现致命漏洞直接跳闸熔断"""
        print(f"\n🔐 [安全网关] 正在将 {len(extracted_deps)} 个虚拟镜像依赖层与本地 CVE 数据库碰撞...")
        
        threats_found = []
        for dep in extracted_deps:
            key = f"{dep['package']}:{dep['version']}"
            if key in CVE_DANGER_DATABASE:
                cve_info = CVE_DANGER_DATABASE[key]
                threats_found.append({
                    "package": dep["package"],
                    "version": dep["version"],
                    "cve": cve_info["cve"],
                    "name": cve_info["name"],
                    "severity": cve_info["severity"]
                })
                
        # 评估是否触发物理熔断拉闸
        has_critical_threat = False
        for threat in threats_found:
            print(f"  🚨 [漏洞查明] 发现依赖 [{threat['package']}] 命中漏洞 {threat['cve']}")
            print(f"     -> 漏洞描述: {threat['name']}")
            print(f"     -> 危害级别: {threat['severity']}")
            
            if threat["severity"] == self.limit:
                has_critical_threat = True
                
        if has_critical_threat:
            print(f"\n{Color.RED}⛔ [FATAL BREAKER] 检测到编译层命中致命漏洞，安全大闸物理熔断，终止构建！{Color.RESET}\n")
            # 物理退出进程，返回安全熔断专用状态码 99
            sys.exit(99)
            
        print("  💚 [安全通过] 镜像依赖层检测合格，无致命 CVE 威胁。")
        return threats_found


# 极简 ANSI 控制台彩色定义辅助，拒绝外部臃肿包
class Color:
    RED = "\033[1;31m"
    RESET = "\033[0m"


# ==================== 仿真运行与测试驱动入口 ====================
if __name__ == "__main__":
    print("[⚙] 正在初始化开源智核 Docker 静态镜像层漏扫与 CVE 熔断引擎...")
    
    parser = DockerfileStaticParser()
    breaker = SecurityCollisionBreaker(target_severity_limit="CRITICAL")

    # 模拟一个因为开发引入过期基础镜像，并打包了致命 log4j 核弹级漏洞的 Dockerfile 文件文本
    mock_dockerfile_content = (
        "FROM ubuntu:18.04\n"
        "LABEL maintainer='devops@company.com'\n"
        "RUN apt-get update && apt-get install -y \\\n"
        "    curl=7.68.0 \\\n"
        "    openssl=1.1.1 \\\n" # 命中致命 CRITICAL 级漏洞
        "    python=3.7\n"       # 命中 HIGH 级漏洞
        "COPY . /app\n"
        "WORKDIR /app\n"
        "CMD ['python', 'app.py']\n"
    )

    # 1. 解析依赖层
    print("\n--------------------------------------------------")
    print("[阶段一：Dockerfile 静态依赖层提取]")
    extracted_deps = parser.extract_dependencies(mock_dockerfile_content)
    print(f" 📂 静态解构出以下待打包依赖配置:")
    for dep in extracted_deps:
        print(f"  -> 类型: {dep['type']:<12} | 包名: {dep['package']:<10} | 版本号: {dep['version']}")

    # 2. 安全漏扫与熔断拉闸
    print("\n--------------------------------------------------")
    print("[阶段二::CVE 数据库碰撞与安全跳闸门禁]")
    
    try:
        threat_reports = breaker.enforce_threat_check(extracted_deps)
    except SystemExit as e:
        # 拦截退出状态码为 99 的熔断拉闸，证明整个安全防御链路 100% 畅通
        if e.code == 99:
            print("[✔ 引擎测试结论] Docker 依赖层扫描、高危 CVE 碰撞与安全熔断拦截 100% 成功！")
            sys.exit(0)
            
    print("[❌ 致命错误] 熔断机制失效，带核弹漏洞的 Docker 镜像已成功打包发布！")
    sys.exit(1)
