import math
import sys

class WiFiCSIBreathingSimulator:
    def __init__(self, sample_rate=20):
        # 设定 Wi-Fi CSI 芯片底层采样率为 20Hz (每秒采样 20 次)
        self.sample_rate = sample_rate

    def simulate_breathing_csi(self, is_normal=True, duration_sec=15.0):
        """工作流一：仿真 Wi-Fi 信号在胸腔微弱震荡（10-20Hz）下的 CSI 振幅波动"""
        num_samples = int(duration_sec * self.sample_rate)
        csi_stream = []
        
        # 正常人呼吸频率约 15次/分钟 (0.25 Hz)
        breathing_freq = 0.25
        
        for i in range(num_samples):
            t = i / self.sample_rate
            
            # 仿真高频环境射频白噪音
            noise = 0.04 * math.sin(2 * math.pi * 5.0 * t) + 0.01 * math.cos(2 * math.pi * 9.0 * t)
            
            if is_normal:
                # 正常呼吸：微弱的 0.25Hz 正弦起伏 + 高频噪声
                amplitude = 1.5 + 0.3 * math.sin(2 * math.pi * breathing_freq * t) + noise
            else:
                # 异常情况：前 4s 呼吸正常，4s 之后突发呼吸骤停窒息（CSI 信号只剩高频噪声）
                if t < 4.0:
                    amplitude = 1.5 + 0.3 * math.sin(2 * math.pi * breathing_freq * t) + noise
                else:
                    amplitude = 1.5 + noise # 呼吸起伏消失
                    
            csi_stream.append((t, amplitude))
            
        return csi_stream


class BreathingApneaDetector:
    def __init__(self, window_size=5, sample_rate=20, flatline_threshold=0.05):
        self.window_size = window_size
        self.sample_rate = sample_rate
        self.flatline_threshold = flatline_threshold # 呼吸起伏波动阈值

    def moving_average_smooth(self, csi_stream):
        """滤波去噪：使用经典低通滑动均值窗口物理去除高频环境噪声"""
        smoothed = []
        raw_vals = [item[1] for item in csi_stream]
        
        for i in range(len(raw_vals)):
            start_idx = max(0, i - self.window_size + 1)
            window_vals = raw_vals[start_idx:i+1]
            smoothed.append(sum(window_vals) / len(window_vals))
            
        return smoothed

    def analyze_respiration(self, csi_stream):
        """工作流二：滑动窗口标准差检测，检测 10 秒无起伏瞬间拉响窒息警报"""
        # 1. 低通滑动均值去噪
        smoothed_vals = self.moving_average_smooth(csi_stream)
        
        # 2. 估计呼吸频率：使用标准的零交叉算法
        global_mean = sum(smoothed_vals) / len(smoothed_vals)
        zero_crossings = []
        for i in range(1, len(smoothed_vals)):
            val_prev = smoothed_vals[i-1] - global_mean
            val_curr = smoothed_vals[i] - global_mean
            if (val_prev < 0 and val_curr >= 0) or (val_prev > 0 and val_curr <= 0):
                zero_crossings.append(csi_stream[i][0])

        # 3. 黄金 10 秒窒息判定：检测最后 10 秒（200 个样本点）的信号标准差（标准波动度）
        num_apnea_samples = int(10.0 * self.sample_rate)
        last_10s_vals = smoothed_vals[-num_apnea_samples:]
        
        # 计算标准差
        mean_10s = sum(last_10s_vals) / len(last_10s_vals)
        variance_10s = sum((x - mean_10s) ** 2 for x in last_10s_vals) / len(last_10s_vals)
        std_dev_10s = math.sqrt(variance_10s)

        # 若最后 10 秒的标准差低于阈值，判定为发生窒息暂停
        is_apnea = std_dev_10s < self.flatline_threshold
        
        # 估算呼吸频率
        num_cycles = len(zero_crossings) / 2.0
        total_time_min = (csi_stream[-1][0] - csi_stream[0][0]) / 60.0
        resp_rate = num_cycles / total_time_min if total_time_min > 0 else 0.0

        return is_apnea, std_dev_10s, resp_rate


# ==================== 仿真物理运行与并发测试入口 ====================
if __name__ == "__main__":
    print("[⚙] 正在初始化 wifi-vital-tracker 无感呼吸相频估计与窒息断路引擎...")
    
    sim = WiFiCSIBreathingSimulator()
    detector = BreathingApneaDetector(flatline_threshold=0.05)

    print("\n--------------------------------------------------")
    print("[场景仿真一：患者正常入睡，平稳呼吸持续 15 秒]")
    normal_data = sim.simulate_breathing_csi(is_normal=True, duration_sec=15.0)
    is_norm_apnea, norm_std, norm_rate = detector.analyze_respiration(normal_data)
    print(f" 📂 CSI 信道状态信息采样完毕，采集点: {len(normal_data)} 个")
    print(f" 📊 估算实时呼吸频率: {norm_rate:.1f} 次/分钟")
    print(f" ⏳ 最后 10 秒呼吸波动标准差: {norm_std:.4f}")
    print(f" 🚨 呼吸安全状态: {'[💥 报警！检测到窒息暂停]' if is_norm_apnea else '[✔ 呼吸平稳正常]'}")

    print("\n--------------------------------------------------")
    print("[场景仿真二：患者突发急性呼吸骤停（第 4 秒开始窒息，持续 11 秒）]")
    apnea_data = sim.simulate_breathing_csi(is_normal=False, duration_sec=15.0)
    is_apnea_alert, apnea_std, apnea_rate = detector.analyze_respiration(apnea_data)
    print(f" 📂 CSI 信道状态信息采样完毕，采集点: {len(apnea_data)} 个")
    print(f" 📊 估算实时呼吸频率: {apnea_rate:.1f} 次/分钟")
    print(f" ⏳ 最后 10 秒呼吸波动标准差: {apnea_std:.4f}")
    print(f" 🚨 呼吸安全状态: {'[💥 报警！检测到窒息暂停]' if is_apnea_alert else '[✔ 呼吸平稳正常]'}")

    # 验证算法是否 100% 准确区分了正常呼吸与 10 秒窒息异常，确保生命安全
    if not is_norm_apnea and is_apnea_alert:
        print("\n--------------------------------------------------")
        print("[✔ 引擎测试结论] Wi-Fi 隔空无感呼吸波形提取与 10 秒窒息断路警报 100% 运行成功！")
        sys.exit(0)
    else:
        print("\n--------------------------------------------------")
        print("[❌ 致命错误] 警报漏判或误报！这在医学监护上是绝对不被允许的！")
        sys.exit(1)
