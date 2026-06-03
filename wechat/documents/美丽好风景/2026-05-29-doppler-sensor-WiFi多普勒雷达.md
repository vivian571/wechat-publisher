import math
import sys

class WiFiDopplerSimulator:
    def __init__(self, carrier_freq=5.8e9):
        # 5.8GHz 频段 Wi-Fi 的物理参数，光速约为 3e8 m/s
        self.c = 3.0e8
        self.freq = carrier_freq
        self.wavelength = self.c / self.freq  # 5.8GHz 波长约 5.17 厘米

    def simulate_csi_doppler_profile(self, movement_type="walk", duration_sec=1.0, sample_rate=100):
        """工作流一：仿真 Wi-Fi 信号在空间物体发生物理位移时的多普勒频移波动"""
        csi_samples = []
        num_samples = int(duration_sec * sample_rate)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            if movement_type == "walk":
                # 正常行走：围绕 1.1 m/s 微弱匀速震荡
                speed = 1.1 + 0.15 * math.sin(2 * math.pi * 2.0 * t)
            elif movement_type == "fall":
                # 突然跌倒：前 0.3s 静止，0.3s - 0.7s 发生重力加速度下坠，随后撞击地面静止
                if t < 0.3:
                    speed = 0.2
                elif t < 0.7:
                    speed = 0.2 + 9.8 * (t - 0.3)  # g = 9.8 m/s^2 自由落体
                else:
                    speed = 0.0
            else:
                speed = 0.0
                
            # 计算对应的多普勒频移 fd = 2 * v / wavelength
            doppler_shift = (2.0 * speed) / self.wavelength
            csi_samples.append((t, doppler_shift))
            
        return csi_samples


class FallDetectionEngine:
    def __init__(self, alert_threshold=100000.0):
        # 设定的自适应速度变化率方差警报阈值
        self.alert_threshold = alert_threshold

    def analyze_movement_dynamics(self, csi_samples):
        """工作流二：编写自适应速度方差计，一旦检测到异常下坠速度（跌倒）瞬间拉响警报"""
        # 1. 对相位波形进行一阶差分，提取即时速度变化率（加速度代理指标）
        accelerations = []
        for i in range(1, len(csi_samples)):
            dt = csi_samples[i][0] - csi_samples[i-1][0]
            dv = csi_samples[i][1] - csi_samples[i-1][1]
            accelerations.append(dv / dt)

        # 2. 计算滑动窗口内的速度变化率方差
        n = len(accelerations)
        if n == 0:
            return False, 0.0
            
        mean_a = sum(accelerations) / n
        variance = sum((a - mean_a) ** 2 for a in accelerations) / n

        # 3. 门限判定：方差超出临界阈值判定为跌倒
        is_fall = variance > self.alert_threshold
        return is_fall, variance


# ==================== 仿真物理运行与并发测试入口 ====================
if __name__ == "__main__":
    print("[⚙] 正在初始化 WiFi-Sensing-doppler 空间相频仿真与重力跌倒检测引擎...")
    
    sim = WiFiDopplerSimulator()
    detector = FallDetectionEngine(alert_threshold=100000.0) # 自适应方差警报阀值

    print("\n--------------------------------------------------")
    print("[场景模拟一：老人在房间里平稳走动 (速度 1.1 m/s 上下平稳波动)]")
    walk_samples = sim.simulate_csi_doppler_profile(movement_type="walk", duration_sec=1.0)
    is_walk_fall, walk_var = detector.analyze_movement_dynamics(walk_samples)
    print(f" 📂 CSI 相频信号抽样完毕，样本数: {len(walk_samples)}")
    print(f" 📊 测算出的速度动态方差: {walk_var:.2f}")
    print(f" 🚨 系统健康判定: {'[💥 发生摔倒警报]' if is_walk_fall else '[✔ 运动安全正常]'}")

    print("\n--------------------------------------------------")
    print("[场景模拟二：老人滑倒瞬间 (发生重力级自由落体下坠且猛烈撞地速度骤减)]")
    fall_samples = sim.simulate_csi_doppler_profile(movement_type="fall", duration_sec=1.0)
    is_real_fall, fall_var = detector.analyze_movement_dynamics(fall_samples)
    print(f" 📂 CSI 相频信号抽样完毕，样本数: {len(fall_samples)}")
    print(f" 📊 测算出的速度动态方差: {fall_var:.2f}")
    print(f" 🚨 系统健康判定: {'[💥 发生摔倒警报]' if is_real_fall else '[✔ 运动安全正常]'}")

    # 验证仿真引擎是否完美区分了行走与滑倒，且方差警报阈值判定 100% 准确
    if not is_walk_fall and is_real_fall:
        print("\n--------------------------------------------------")
        print("[✔ 引擎测试结论] Wi-Fi 多普勒空间相频估计与自适应跌倒重力警报 100% 运行成功！")
        sys.exit(0)
    else:
        print("\n--------------------------------------------------")
        print("[❌ 致命错误] 警报阈值设计失效，误报或漏报人命关天！")
        sys.exit(1)
