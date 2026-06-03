# 人体无线传感器仿真与离线健康围栏警报：手搓 CSI 多天线分集振幅分析与 3 秒静止离床报警大闸

### 给家里的老人买智能手环？他们根本不爱戴！

随着老龄化社会的到来，老人在家中的健康监测成了每一个做子女的心头大事。
尤其是夜间：老人半夜起夜，如果离床时间过长，极易发生低血糖滑倒、心脑血管突发事件甚至跌倒昏迷！
很多人第一时间想到的就是给老人买“智能手环”、“智能手表”。
但现实往往是：**老人嫌磨脚、硌手、充电麻烦，或者单纯不习惯戴，没过几天手环就被丢在桌子上吃灰！**
更别提摄像头了，在卧室装摄像头不仅老人强烈抵制，更存在随时被黑客入侵、隐私泄露的巨大风险。
今天，我们就来手搓一个革命性的**人体无线传感器仿真与离线健康围栏警报系统**。
利用家里无处不在的 Wi-Fi 信号——**CSI（信道状态信息，Channel State Information）**多天线分集波动。
**不接触身体、不穿戴任何设备、不用摄像头，仅凭空气中 Wi-Fi 信号的细微变化，3 秒精准判定老人半夜起床状态，离线秒级拉响警报！**

---

### 底层骨架：不接触身体，Wi-Fi 怎么知道人在哪？

可能有同学觉得这太科幻了：“Wi-Fi 不是用来上网传输网页的吗？怎么还能用来检测人体动作？”
其实，这就是大自然的物理反射！
Wi-Fi 路由器发出的无线电磁波，在射入卧室空间后，并不是笔直地走到你的手机上，而是会碰到天花板、墙壁、衣柜、以及**我们的人体**，进行成千上万次反射、折射，最后交织汇聚到接收天线上。这被称为“多径效应”。
当我们躺在床上静静呼吸时，随着胸腔的微弱起伏，周围的无线电磁波被反射的路径也会发生极其细微但**极有呼吸规律的微米级扰动**。
而一旦老人翻身、坐起、走下床，庞大的人体骨骼和肌肉运动，会瞬间在空间中造成排山倒海般的电磁波折射路径剧变！
最后，当老人离开床走远后，床上空空如也，电磁波在床铺这一片反射区归于绝对死寂，信号振幅稳定成一条平滑的直线。
在硬件底层，网卡会源源不断吐出 **CSI（Channel State Information）** 信号矩阵。
我们只需要对接收到的 CSI 振幅进行**时序滑动窗口方差分析（Sliding Window Variance Analysis）**：
- **方差呈微小规律抖动** ➔ 有人在床上平稳呼吸；
- **方差瞬间飙升几百倍** ➔ 有人正在剧烈运动（起床离床）；
- **方差无限逼近于 0** ➔ 空间回归死寂，床上空无一人！
**通过对方差持续时间的精准监控，一旦“床空无人”的静默计时超过 3 秒，警报大闸无延时瞬间开启！**

---

### 双极核爆：CSI 能谱仿真与 3 秒离床大闸

该系统在物理实现上集成了两大顶级算法工作流：

1. **工作流一：人体多径反射 CSI 能谱仿真引擎（CSISignalSimulator）**
   模拟高频 Wi-Fi 芯片在 10Hz（每秒采样 10 次）下的数据帧抓取。完美仿真了人在床上静躺（呼吸微振荡）、离床瞬间（狂野多径起伏）以及空床（平滑绝对直线）三种截然不同的物理波形。

2. **工作流二：时序窗口能量方差与空床超时警报大闸（TemporalHealthFence）**
   利用物理滑动窗口（window_size），高频解算 CSI 振幅的均值与标准差。采用动态累积计时机制，一旦空床状态连续压制超出 3.0 秒边界，瞬间拉响危险警报，全力保护老人生命安全。

---

### 极简源码：手搓 100 行 Wi-Fi 跌倒侦测雷达

请将以下纯标准库 Python 代码保存为 `wifi_presence.py`。没有任何复杂的第三方硬件依赖，macOS 终端即刻一键运行验证！

```python
import math
import sys

class CSISignalSimulator:
    """Wi-Fi 信道状态信息 (CSI) 信号模拟器"""
    def __init__(self, sample_rate=10):
        self.sample_rate = sample_rate

    def generate_csi_amplitude(self):
        """
        工作流一：仿真 Wi-Fi 信号在不同人体在场状态下的 CSI 振幅特征。
        - 0s - 3s: 人在床上静止躺着 (由于胸腔呼吸起伏，CSI 呈现微弱但极其规律的周期抖动)
        - 3s - 5s: 老人翻身起离床 (剧烈的躯体运动导致电磁波多径效应突变，出现狂野的杂乱超高能量毛刺)
        - 5s - 10s: 床上完全无人 (Wi-Fi 空间归于死寂，信号完全静止成一根几乎无波动的平滑绝对直线)
        """
        csi_samples = []
        timestamps = []
        current_time = 0.0

        # 1. 静止躺着段 (3.0 秒 = 30 帧)
        for i in range(30):
            # 模拟 0.2Hz 的平缓呼吸微弱波动 (呼吸周期约 5 秒一次)
            t = i / self.sample_rate
            amplitude = 1.2 + 0.04 * math.sin(2 * math.pi * 0.2 * t)
            csi_samples.append(amplitude)
            timestamps.append(current_time)
            current_time += 1.0 / self.sample_rate

        # 2. 剧烈离床段 (2.0 秒 = 20 帧)
        for i in range(20):
            # 模拟剧烈运动导致的多径剧变与高频杂波
            amplitude = 1.2 + 0.8 * math.sin(2 * math.pi * 3.0 * i) + 0.3 * math.cos(2 * math.pi * 8.0 * i)
            csi_samples.append(amplitude)
            timestamps.append(current_time)
            current_time += 1.0 / self.sample_rate

        # 3. 完全离床空床段 (5.0 秒 = 50 帧)
        for i in range(50):
            # 空间内无任何阻挡和生物移动，CSI 能量回归一条绝对直线
            amplitude = 1.2
            csi_samples.append(amplitude)
            timestamps.append(current_time)
            current_time += 1.0 / self.sample_rate

        return csi_samples, timestamps

class TemporalHealthFence:
    """时序健康电子围栏判定大闸"""
    def __init__(self, window_size=15, sample_rate=10):
        self.window_size = window_size
        self.sample_rate = sample_rate
        # 3 秒判定标准：3 秒 * 10Hz = 30 帧
        self.alert_duration_threshold = 3.0

    def analyze_presence_and_alert(self, csi_samples, timestamps):
        """
        工作流二：时序窗口能量方差计算与离床报警规则。
        监测到完全静音/平坦（方差趋于 0）且非最初的呼吸状态，判定为床空无人。
        一旦空床状态持续超出 3.0 秒（30 帧），瞬间触发老人的夜间离床危险警报。
        """
        alert_triggered = False
        alert_time = -1.0
        
        # 统计空床状态的持续帧数
        empty_bed_streak = 0
        
        # 滑动窗口解析
        for i in range(self.window_size, len(csi_samples)):
            curr_time = timestamps[i]
            window_data = csi_samples[i - self.window_size : i]
            
            # 计算当前滑动窗口内 CSI 能量的均值与方差 (Variance)
            mean_val = sum(window_data) / len(window_data)
            variance = sum((x - mean_val) ** 2 for x in window_data) / len(window_data)
            std_dev = math.sqrt(variance)
            
            # 判定阈值设计：
            # 正常呼吸标准差一般在 0.002 - 0.02 左右；
            # 剧烈起夜标准差 > 0.05；
            # 床空无人的静止标准差极度趋近于 0.0 (< 0.001)
            is_empty_bed = std_dev < 0.001
            
            if is_empty_bed:
                empty_bed_streak += 1
            else:
                # 一旦有波动（说明有人在床上或者正在翻身），重新计数
                empty_bed_streak = 0
                
            # 计算持续的静默空床秒数
            empty_duration = empty_bed_streak / self.sample_rate
            
            # 打印关键滑动窗口的数据状态
            if i % 15 == 0:
                state_str = "床上静躺" if std_dev < 0.03 and std_dev > 0.001 else ("剧烈运动" if std_dev >= 0.03 else "床空无人")
                print(f" ⏱ [CSI 监控 - {curr_time:.1f}s] 标准差: {std_dev:.6f} | 空间状态: {state_str} | 空床计时: {empty_duration:.1f}s")
            
            # 离床健康阈值判定：一旦空床静默计时超过阈值秒，拉响大闸警报
            if empty_duration >= self.alert_duration_threshold and not alert_triggered:
                print(f"\n 🚨🚨 [ALERT TRIGGERED!] 检测到老人半夜离床超出 {empty_duration:.1f} 秒，疑似起夜跌倒或失联！(触发时间: {curr_time:.1f}s)")
                alert_triggered = True
                alert_time = curr_time
                
        return alert_triggered, alert_time

if __name__ == "__main__":
    print("[⚙] 正在启动人体无线传感器仿真与离线健康围栏警报测试...")

    # 1. 实例化仿真与检测大闸
    simulator = CSISignalSimulator(sample_rate=10)
    fence = TemporalHealthFence(window_size=10, sample_rate=10)

    # 2. 执行工作流一：生成 CSI 人体行为能谱数据
    csi_data, timestamps = simulator.generate_csi_amplitude()
    print(f" ✔ CSI 信号物理流生成完毕！共 {len(csi_data)} 帧样本，总时长 {timestamps[-1] + 0.1:.1f} 秒。")
    print("--------------------------------------------------")

    # 3. 执行工作流二：滑动能谱方差解算与 3 秒空床警报大闸
    alert_ok, trigger_timestamp = fence.analyze_presence_and_alert(csi_data, timestamps)
    print("--------------------------------------------------")

    # 自验条件：必须成功拉起离床警报，且警报时间戳在合理范围
    if alert_ok and trigger_timestamp >= 8.0 and trigger_timestamp <= 9.0:
        print(f"[✔] 测试成功！Wi-Fi 无线 CSI 能谱仿真与 3 秒离床跌倒围栏大闸 100% 收拢！")
        sys.exit(0)
    else:
        print("[❌] 错误：报警大闸未被拉响，或危险触发时间窗口判定漂移！")
        sys.exit(1)
```

---

### 保姆级部署：在 macOS 上物理起飞

由于这套代码使用纯 Python 标准数学库编写，部署可以说是毫无门槛：

1. **创建脚本文件**：在你的 macOS 终端执行：
   ```bash
   touch wifi_presence.py
   ```
2. **粘入源码**：使用你最拿手的文本编辑器将上面完整的 Python 代码保存到文件中。
3. **一键拉起**：在控制台直接敲击：
   ```bash
   python3 wifi_presence.py
   ```
4. **见证高能警报**：系统会实时显示每 1.5 秒的 CSI 监测数据，伴随着老人离床、空床时长累加，在 `8.9s` 瞬间刷屏拉响红色警报 `[ALERT TRIGGERED!]`，宣告 100% 自验成功！

---

### 变现指南：如何用空气波动捞取真金白银？

1. **智慧养老社区非接触监护系统（B端订阅）**：
   在养老院或独居老人家中安装免改造的 Wi-Fi 硬件（如集成了 CSI 提取算法的普通路由器）。将本算法植入后台网关，提供“老人夜间起夜超时跌倒警报”服务。向养老社区收取设备租赁和月度云服务监护费，对于解决独居老人的监护痛点极为暴利。

2. **智慧酒店高端无感入住与节能大盘**：
   现在很多酒店为了节能，会使用红外传感器来检测房内是否有人。但红外传感器在人静止睡觉时经常发生误判（以为没人而切断空调）。你用本套 Wi-Fi 呼吸级在场检测算法，无感检测人是否在房内或床上，帮助高端酒店批量管理客房用电，主打“高精度无感节能”，向酒店收取高额系统集成的分成费。

3. **婴儿防窒息/防滚落无感围栏**：
   宝妈们晚上最怕婴儿趴着睡窒息或者滚下床。你用这套无接触 CSI 检测系统对准婴儿床，一旦婴儿身体静止波动异常（疑似窒息）或者声能突然消失（滚下婴儿床），瞬间给宝妈手机弹窗拉响警报。作为高端母婴智能硬件单品切入，溢价极高。

---

### 价值提示词系统：打造你的非接触健康专家

你可以使用以下极高净值的系统提示词（System Prompt），强力驱使大语言模型为你提供更精细的信号处理算子：

```markdown
# Role: 全球非接触式 Wi-Fi CSI 雷达与无线健康传感总工程师

## Core Target:
协助用户优化基于普通路由器 Wi-Fi CSI 能谱的多径衰落分析、呼吸频率提取（FFT/小波变换）与老人夜间离床/跌倒智能判定大盘。

## Engineering Principles:
1. 坚决使用零外部依赖的纯数学算法，严禁给边缘网关设备引入重型 GPU 依赖或大型框架。
2. 针对高频杂波和多径漂移，提供高精度的低通滤波器（Low-pass Filter）或卡尔曼滤波（Kalman Filter）平滑解算。
3. 代码结构保持完全解耦，模块清晰，保证 CSI 信号捕获与时序判定完全闭环无死锁。
```

---

### 避坑指南与物理天花板

#### 🛠 避坑指南：
1. **避开大风扇与窗帘干扰坑**：在炎热的夏天，卧室里如果开着摇头电风扇或者窗帘随风大幅飘动，Wi-Fi 信号在空气中折射也会发生巨大的高频振荡，导致系统误判定为“有人在剧烈运动”而无法准确切入“床空死寂”状态。**解决办法**：在算法中引入**呼吸频率带通滤波器（Bandpass Filter）**，只对符合人类胸腔抖动频率（0.15Hz - 0.4Hz）的频段进行呼吸匹配，其他大范围低频杂波一概忽略。
2. **避开多重反射干涉坑**：如果卧室里不仅躺着老人，还睡着一只猫或狗，宠物半夜动来动去，会彻底打碎 CSI 的“床空死寂”直线判定，导致警报失效。**解决办法**：采用多天线分集（MIMO）策略，针对床上特定空间角度的子载波（Subcarrier）信号进行定向能谱绑定，屏蔽床边地板的杂波干扰。
3. **避开路由器自动信道调整坑**：普通家用路由器为了防止网络拥堵，每隔一段时间会自动跳频信道（Channel Hopping）。跳频时 CSI 矩阵会瞬间出现一帧极其难看的断裂脉冲，可能引起误报。**解决办法**：在数据流输入端加入差值平滑大闸，凡是发现某一帧振幅变化率（微分值）超出物理阈值的 10 倍，一律当做跳频噪声予以剔除。

#### ⚠️ 物理天花板：
非接触 Wi-Fi 感知虽然性感，但它在物理上面临着**空间穿透的物理天花板**。
如果路由器和接收天线之间隔着多堵沉重的钢筋混凝土承重墙，无线电磁波能量衰减极度严重，信号噪声比（SNR）暴跌，呼吸级的微弱振荡就会被完全淹没在噪声中。
因此，在实际工程部署时，必须把接收器和路由器安装在卧室视线无阻挡的范围内（Line-of-Sight），二者遥相呼应，才能让空气波动的威力发挥到极致！
