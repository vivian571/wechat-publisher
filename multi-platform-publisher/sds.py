import turtle
import random
import time
import math

# --- 系统初始化 ---
screen = turtle.Screen()
screen.setup(900, 700)
screen.bgcolor('black')
screen.title("To Yi An: The Ultimate Cyber-Christmas System")
screen.tracer(0)  # 关闭自动渲染，完全手动接管每一帧

# --- 定义专职画笔 (Turtles) ---
# 静态层画笔
tree_pen = turtle.Turtle()
tree_pen.hideturtle()
text_pen = turtle.Turtle()
text_pen.hideturtle()

# 动态层画笔 (每一帧都会重绘)
snow_pen = turtle.Turtle()
snow_pen.hideturtle()
light_pen = turtle.Turtle()
light_pen.hideturtle()
star_pen = turtle.Turtle()
star_pen.hideturtle()

# ===========================
# --- 静态结构层 (Static Layer) ---
# ===========================

# 画松树的一层三角形
def draw_layer(t, width, height, color):
    t.fillcolor(color)
    t.begin_fill()
    t.forward(width / 2)
    t.left(120)
    t.forward(width)
    t.left(120)
    t.forward(width)
    t.left(120)
    t.forward(width / 2)
    t.end_fill()

# 画完整的静态树体
def draw_static_tree():
    # 树干
    tree_pen.penup()
    tree_pen.goto(15, -250)
    tree_pen.pendown()
    tree_pen.color("sienna")
    tree_pen.begin_fill()
    for _ in range(2):
        tree_pen.right(90)
        tree_pen.forward(50)
        tree_pen.right(90)
        tree_pen.forward(30)
    tree_pen.end_fill()

    # 树叶
    y = -250
    width = 260
    height = 100
    for _ in range(3):
        tree_pen.penup()
        tree_pen.goto(0, y)
        tree_pen.setheading(0)
        tree_pen.pendown()
        tree_pen.color("#0F3B0F", "#228B22") # 更深邃的森林绿
        draw_layer(tree_pen, width, height, "#228B22")
        y += 90
        width -= 70

# 写下那句永恒的底层逻辑
def write_message():
    text_pen.penup()
    text_pen.goto(0, -320)
    # 使用一种带有赛博感的亮粉色
    text_pen.color("#FF1493") 
    text_pen.write("以安，整个系统都在为你闪烁", align="center", font=("Microsoft YaHei", 18, "bold"))
    # 再写一层制造发光感
    text_pen.goto(2, -322)
    text_pen.color("#FF69B4")
    text_pen.write("以安，整个系统都在为你闪烁", align="center", font=("Microsoft YaHei", 18, "bold"))

# ===========================
# --- 动态逻辑层 (Dynamic Layer) ---
# ===========================

# 1. 粒子雪花系统
snowflakes = []
def init_snow():
    for _ in range(150): # 生成150片雪花
        # [x坐标, y坐标, 下落速度, 大小]
        snowflakes.append([random.randint(-450, 450), random.randint(-350, 350), random.uniform(1, 3), random.randint(2, 5)])

def update_snow():
    snow_pen.clear() # 清除上一帧
    snow_pen.color("white")
    for flake in snowflakes:
        flake[1] -= flake[2] # 向下移动
        # 如果落出屏幕底部，重置到顶部
        if flake[1] < -350:
            flake[1] = 350
            flake[0] = random.randint(-450, 450)
        
        snow_pen.penup()
        snow_pen.goto(flake[0], flake[1])
        snow_pen.dot(flake[3]) # 绘制

# 2. 辉光灯效系统
light_positions = []
light_colors = ["#FF0000", "#FFFF00", "#00FFFF", "#FF00FF", "#FFFFFF", "#FFA500", "#00FF00"]
# 辉光映射表：给每个主色配一个暗一点的辉光色
glow_map = {
    "#FF0000": "#8B0000", "#FFFF00": "#B8860B", "#00FFFF": "#008B8B",
    "#FF00FF": "#8B008B", "#FFFFFF": "#A9A9A9", "#FFA500": "#FF8C00", "#00FF00": "#006400"
}

def init_lights():
    # 在树的范围内生成灯光位置
    start_y = -230
    for i in range(70):
        y_pos = random.randint(-230, 40)
        width_limit = 110 - (y_pos + 230) * 0.4
        x_pos = random.randint(int(-width_limit), int(width_limit))
        # [x, y, 当前颜色, 目标颜色]
        c = random.choice(light_colors)
        light_positions.append([x_pos, y_pos, c, c])

def update_lights(frame_count):
    light_pen.clear()
    
    # 每隔几帧随机改变一些灯的目标颜色
    if frame_count % 10 == 0:
        for _ in range(15):
            chosen_light = random.choice(light_positions)
            chosen_light[3] = random.choice(light_colors)

    for light in light_positions:
        # 简单的颜色过渡逻辑 (直接切换，为了更有赛博感)
        light[2] = light[3] 
        
        light_pen.penup()
        light_pen.goto(light[0], light[1])
        
        # --- 核心：绘制辉光 (Bloom) ---
        # 先画一个大一点、暗一点的圆在后面
        light_pen.dot(16, glow_map.get(light[2], "gray"))
        # 再画一个小一点、亮一点的圆在前面
        light_pen.dot(9, light[2])

# 3. 脉冲核心之星
def update_star(frame_count):
    star_pen.clear()
    # 利用正弦波计算脉冲大小，制造呼吸感
    # 大小在 35 到 45 之间波动
    size = 40 + math.sin(frame_count * 0.1) * 5 
    
    star_pen.penup()
    star_pen.goto(-size/2 + 2, 50) # 稍微调整中心
    star_pen.color("#FFD700", "#FFFFE0") # 金色边框，亮黄填充
    star_pen.pendown()
    star_pen.begin_fill()
    for _ in range(5):
        star_pen.forward(size)
        star_pen.right(144)
    star_pen.end_fill()
    
    # 添加星星的辉光
    star_pen.penup()
    star_pen.goto(0, 50 - size*0.1) # 大致中心
    # 画一个半透明的黄色大圆晕 (Turtle无法真透明，用散点模拟)
    star_pen.color("#FFFF00")
    for _ in range(10):
        star_pen.goto(random.randint(-5, 5), 50 + random.randint(-5, 5))
        star_pen.dot(size * 1.5)

# ===========================
# --- 主程序引擎 (Main Engine) ---
# ===========================

# 1. 绘制静态世界
draw_static_tree()
write_message()

# 2. 初始化动态元素
init_snow()
init_lights()

# 3. 启动无限循环引擎 (The Loop)
frame = 0
try:
    while True:
        # --- 每一帧的更新逻辑 ---
        update_snow()
        update_lights(frame)
        update_star(frame)
        
        # --- 渲染这一帧 ---
        screen.update() 
        
        # --- 控制帧率 (约30FPS) ---
        time.sleep(0.03)
        frame += 1
        
except turtle.Terminator:
    # 优雅退出
    print("系统已关闭。以安，光芒永在。")py