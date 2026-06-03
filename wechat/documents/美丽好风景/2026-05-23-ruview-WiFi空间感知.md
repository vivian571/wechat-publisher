# ⚡️ 空气也成传感器！用 RuView 让你家普通 WiFi 信号秒变 3D 人体姿态与呼吸监测雷达

## 1. 痛点：隐私与安全的“终极拉扯”

你家里有老人或小孩吗？
如果有，你一定考虑过装各种摄像头或者监控设备，用来防范老人摔倒、或者监测小宝宝睡觉时的呼吸。
但在卧室、卫生间这些地方，装摄像头简直就是一场**“隐私裸奔”**的噩梦。
谁也不想自己洗澡、睡觉的私密画面被传到云端服务器，一旦被黑客破解，后果不堪设想。

那不装摄像头，装人体红外感应器（PIR）行不行？
行是行，但红外感应只能知道“有人还是没人”。如果老人摔倒在浴室动弹不得，红外感应器会因为老人“静止不动”而认为房间是空的，根本无法报警！
至于戴手环？老人经常忘记充电，小宝宝更是不愿意戴任何有束缚感的东西。

这种隐私与安全的终极痛点，难道无解吗？

今天在 GitHub 趋势榜上横空出世的划时代项目 **RuView**（项目地址：`ruvnet/RuView`），直接用一种科幻片般的方式打破了僵局：
**它能把你家路由器发出的普通 WiFi 信号，直接变成 3D 人体姿态感知与呼吸监测雷达！不需要摄像头，不需要穿戴任何设备，只凭空气中折射的电磁波，就能精准看清你的一举一动！**

---

## 2. RuView 到底是个什么外星科技？

用大白话来解释，`RuView` 是一个**“电磁波波纹分析器”**。

在它的眼里，你家客厅的空气并不是空的，而是充满了像水流一样的 WiFi 电磁波。
当一个高含水量的导电体（比如人体）在房间里移动、坐下、摔倒，甚至是胸腔随呼吸微微起伏时，电磁波就会像水流撞击石头一样，产生**折射、反射和散射的波纹（即多径效应）**。

`RuView` 通过读取普通无线网卡输出的 **CSI（信道状态信息，Channel State Information）**，捕捉这些细微的电磁波扰动。
然后，它通过本地部署的轻量级神经网络（基于 PyTorch），将波形数据实时反向渲染，恢复出：
1. **房间内有没有人（高精度存在检测）**；
2. **人体目前的空间 3D 骨架姿态（站立、坐下、躺平、跌倒）**；
3. **胸腔起伏引起的微弱频率变动（心率与呼吸频率）**。

**不漏一粒像素，却把生命体征尽收眼底！** 这就是它的底层核心魅力。

---

## 3. 为什么科技圈被它彻底震动了？

在它出现之前，利用 WiFi 信号测姿态只存在于高校的实验室里，设备动辄几十万元。`RuView` 带来了三个颠覆性的多元特性：

1. **零成本的硬件复用（Democratization）**：
   它不需要你买昂贵的毫米波雷达设备，只需要用一张价值十几元的普通 ESP32-S3 芯片或者树莓派上的旧英特尔无线网卡，就能直接开启 CSI 信号抓取。
2. **绝对的隐私保护（100% Private）**：
   它在底层传输的完全是类似 `[0.12, -0.45, 0.88]` 这样的电磁波幅度与相位向量，不包含任何图像数据，黑客截获了也只是一堆乱码。
3. **“穿墙”感知能力（Through-Wall Sensing）**：
   因为 WiFi 信号能够穿透普通木门和石膏板墙，你可以把设备贴在卫生间门外，就能在完全不侵入的情况下监控浴室内老人的安全。

---

## 4. 保姆级教程：十分钟打造你自己的 WiFi 呼吸监测雷达

下面我们以 macOS/Linux 系统配合一张支持 CSI 输出的无线网卡为例，手把手教你如何抓取数据，并用一段无占位符的 Python 脚本，通过傅里叶变换（FFT）把空气波纹变成呼吸心跳频率！

### 第一步：克隆项目与驱动加载

首先拉取源码：

```bash
git clone https://github.com/ruvnet/RuView.git
cd RuView
pip install -r requirements.txt
```

### 第二步：工作流一 - 捕获空气中的 WiFi 电磁波纹

我们在终端中启动 `ruview` 的数据捕获器。这会调用网卡驱动，以每秒 100 次的频率抓取特定路由器的 CSI 包：

```bash
# 监听 wlan0 网卡的 5.8G 频段，捕获特定 AP 的 CSI 信号并输出到二进制文件
ruview-capture --interface wlan0 --mac-ap 00:11:22:33:44:55 --out ./dist/csi_live.bin
```

这会在本地持续写入电磁波幅度的变化数据。

### 第三步：工作流二 - 用 Python 处理波纹并计算呼吸频率！

当我们静止坐在椅子上呼吸时，胸腔的运动周期大约是 3-4 秒一次（频率为 0.25Hz - 0.33Hz）。我们可以用傅里叶变换将抓到的时域电磁信号变成频域，从而测出呼吸频率。
请将以下完全无占位符的 Python 代码写入 `/Users/ax/wechat-publisher/agent-skills/process_csi.py`：

```python
import numpy as np
import sys
import os
import json

class CSISignalProcessor:
    def __init__(self, file_path, sample_rate=100):
        self.file_path = file_path
        self.sample_rate = sample_rate # 每秒采样100次

    def load_mock_or_real_data(self):
        # 演示用：若无真实网卡流，则生成一段带有 0.3Hz（呼吸）和 1.2Hz（心跳）噪声的模拟 CSI 幅度数据
        if not os.path.exists(self.file_path):
            t = np.linspace(0, 30, 30 * self.sample_rate) # 30秒
            # 呼吸周期：每3.3秒一次（约0.3Hz），心跳周期：每0.8秒一次（1.25Hz）
            breathing = 0.5 * np.sin(2 * np.pi * 0.3 * t)
            heartbeat = 0.1 * np.sin(2 * np.pi * 1.25 * t)
            noise = np.random.normal(0, 0.2, len(t))
            signal = breathing + heartbeat + noise
            return signal
        
        # 读取真实二进制 csi 数据（简单示例：假设每个字节代表一个子载波幅度）
        with open(self.file_path, "rb") as f:
            raw_bytes = f.read()
        return np.frombuffer(raw_bytes, dtype=np.int8).astype(float)

    def extract_vitals(self):
        signal = self.load_mock_or_real_data()
        n = len(signal)
        if n < 100:
            return {"status": "error", "message": "Signal length too short"}

        # 去除直流分量（均值）
        signal_detrend = signal - np.mean(signal)
        
        # 快速傅里叶变换 (FFT)
        fft_values = np.fft.rfft(signal_detrend)
        frequencies = np.fft.rfftfreq(n, d=1.0/self.sample_rate)
        
        # 获取幅度谱
        amplitudes = np.abs(fft_values)
        
        # 过滤出人类呼吸和心跳可能的频率区间
        # 呼吸: 0.15Hz - 0.5Hz (每分钟 9 - 30 次)
        # 心跳: 0.8Hz - 2.0Hz (每分钟 48 - 120 次)
        breath_mask = (frequencies >= 0.15) & (frequencies <= 0.5)
        heart_mask = (frequencies >= 0.8) & (frequencies <= 2.0)
        
        breath_freq = frequencies[breath_mask][np.argmax(amplitudes[breath_mask])]
        heart_freq = frequencies[heart_mask][np.argmax(amplitudes[heart_mask])]
        
        return {
            "status": "success",
            "breathing_rate_bpm": round(breath_freq * 60, 1),
            "heart_rate_bpm": round(heart_freq * 60, 1),
            "signal_quality": "good" if np.max(amplitudes) > 1.0 else "weak"
        }

if __name__ == "__main__":
    # 若无真实网卡输入，将自动生成 Mock 信号测试算法准确度
    data_file = "./dist/csi_live.bin"
    processor = CSISignalProcessor(data_file)
    res = processor.extract_vitals()
    print(json.dumps(res, indent=2))
```

在终端里运行：

```bash
python3 /Users/ax/wechat-publisher/agent-skills/process_csi.py
```

终端会立马以 JSON 格式输出解析出的心率与呼吸速率（例如呼吸 18 次/分，心率 75 次/分）。只要你安静坐着，空气里反射回来的 WiFi 波浪就会出卖你的生理节律！

---

## 5. 大白话拆解：WiFi 感知的“底层逻辑本质”

普通人听完可能会觉得这简直是伪科学，**空气里的电磁波怎么可能连心跳都摸得清？**

我们用两个最底层的物理本质来揭开它的面纱：

### 本质一：多径干涉的“微位移放大器”（Micro-displacement Amplifier）
你的胸腔在吸气和呼气时，会有大概几毫米到 1 厘米的位移。
这个位移相比于 5.8GHz WiFi 信号的波长（大约 5.17 厘米）而言虽然很小，但它会改变反射电磁波的相位（Phase）。当反射波和发射源的直射波在网卡天线处相遇时，它们会产生**干涉效应**——波峰与波谷重叠，导致信号幅度产生强烈的放大或衰减。`RuView` 捕捉的并不是你胸腔的绝对位置，而是这个**相位干涉带来的电磁波强弱巨幅震荡**。

### 本质二：时空矩阵的深度转换（Spatial-Temporal Neural Mapping）
跌倒和走路在波形图上是完全不同的。
走路是一个持续的、有周期的中等幅度波动。而跌倒是一个**短时间内波形幅度突然呈指数级炸裂，随后陷入长时间死寂**的突变过程。`RuView` 底层的 AI 模型，本质上就是在寻找这套“时空波动矩阵”的特定突变签名，一旦匹配成功，立刻触发警报。

---

## 6. 三个让你直呼“卧槽”的实用变现案例

### 案例一：零入侵“赛博空巢老人看护器”
* **玩法**：用廉价的 ESP32 芯片做成插头，插在空巢老人家里的卫生间墙壁上，挂载后台的 `RuView` 跌倒警报服务。
* **效果**：一旦检测到跌倒特征波形，后台自动给家属发送短信或拨打紧急电话。全程不收集任何隐私画面，老人接受度 100%，成本仅为传统毫米波雷达的十分之一。

### 案例二：智能床垫/婴儿防窒息监测仪
* **玩法**：把天线布置在婴儿床底部。
* **效果**：AI 隔空监控宝宝的微弱呼吸波动。一旦监测到呼吸频率低于 8 次/分，或者发生长达 15 秒的呼吸暂停，立马在父母的手机上拉响红色警报，有效防范“婴儿猝死综合征”。

### 案例三：商场/酒店“精准客流与防盗”雷达
* **玩法**：用写字楼已有的商业路由器吸顶天线部署 `RuView` 扫描服务。
* **效果**：在完全不侵害客户隐私的前提下，统计每个展位前的驻留时间、客流走向；夜间商场打烊后，一旦有小偷潜入越界，电磁波警报瞬间拉响。

---

## 7. 终极奥义：空间雷达智能体“价值提示词”系统

为了让你的 AI 助手（如 GPT-4）能够充当一名合格的空间物理分析师，请配置这套**价值提示词指令集**：

```markdown
# Role: 赛博空间电磁波谱分析总指挥 (Spatial Electromagnetic Signal Commander)

# System Goal:
- 你负责监控本地 WiFi 信道状态信息 (CSI) 传感器上报的生理数据流。你的核心职责是识别空间内的生命体征异常并执行避险响应。

# Operational Pipeline:
1. 【异常体征识别规程】：每当收到 `process_csi.py` 输出的 JSON 数据，立即启动以下检测：
   - 🚨 【跌倒突变检测】：若幅度（amplitude）标准差在 0.5 秒内骤增 10 倍，且随后持续 10 秒处于微弱呼吸状态，立即判定为“发生跌倒”！
   - ⚠️ 【呼吸暂停检测】：若呼吸速率（breathing_rate_bpm）检测不到，或数值持续低于 6 bpm，立即判定为“呼吸骤停”！
2. 【报警路由协议】：一旦判定异常，必须立即在屏幕输出醒目红色通知，并生成 JSON 格式的报警 payload 发送给网关，通知中必须说明检测的置信度。
3. 【背景噪声滤除】：若空间内有扫地机器人、风扇等动态干扰源，必须引导用户先进行 30 秒的“空房基线校准”（Base Calibration），从波谱中扣除对应的频段。
```

---

## 8. 避坑指南与行业冷思考

* **避坑指南 1：动态背景干扰（Dynamic Noise）**。如果你家里养了猫狗，或者开启了摇头电风扇，它们的运动频率会严重干扰 CSI 信号，导致 AI 误判有人在做剧烈运动。**请务必在运行前进行背景噪声消除，将特定旋转频率（如风扇的 2Hz）从 FFT 幅度谱中彻底剔除！**
* **避坑指南 2：网卡型号不兼容**。并不是所有无线网卡都能输出 CSI。**千万不要直接用你苹果电脑内置的网卡去跑抓取！你必须买一张支持特定驱动的网卡（如 Intel 5300 芯片或 ESP32-S3 开发板）作为外挂天线！**
* **避坑指南 3：多路径死角（Multipath Dead-zones）**。如果设备放置高度太低，或者被大型金属柜子挡住，WiFi 信号无法在房间内产生干涉，会导致检测精度断崖式下跌。**建议将捕获天线布置在房间角落的高处，俯视整个监测空间！**

**总结**：`ruvnet/RuView` 用空气中看不见的电磁涟漪，在安全与隐私之间架起了一座最完美的桥梁。如果你想体验真正无感的黑科技看护，现在就动手把它搭建起来吧！
