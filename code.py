import time
import board
import busio
import digitalio
import neopixel
import random
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306
import adafruit_adxl34x

# 兼容性处理
try:
    import i2cdisplaybus
except ImportError:
    import displayio as i2cdisplaybus

# ================= 1. 软件旋钮驱动 =================
class SoftwareEncoder:
    def __init__(self, pin_a, pin_b):
        self.pa = digitalio.DigitalInOut(pin_a); self.pa.pull = digitalio.Pull.UP
        self.pb = digitalio.DigitalInOut(pin_b); self.pb.pull = digitalio.Pull.UP
        self.pos = 0; self.ls = (self.pa.value << 1) | self.pb.value
    def update(self):
        s = (self.pa.value << 1) | self.pb.value
        if s != self.ls:
            if (self.ls==0 and s==1) or (self.ls==1 and s==3) or (self.ls==3 and s==2) or (self.ls==2 and s==0): self.pos += 1
            elif (self.ls==0 and s==2) or (self.ls==2 and s==3) or (self.ls==3 and s==1) or (self.ls==1 and s==0): self.pos -= 1
            self.ls = s

# ================= 2. 硬件初始化 =================

displayio.release_displays()

# I2C (SCL=D5, SDA=D4)
i2c = busio.I2C(board.D5, board.D4)

# OLED 初始化
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

main_group = displayio.Group()
display.root_group = main_group

# ADXL 初始化
accel = None
try:
    accel = adafruit_adxl34x.ADXL345(i2c)
except:
    pass 

# 旋钮 & 按钮
encoder = SoftwareEncoder(board.D0, board.D1)
last_pos_global = 0
button = digitalio.DigitalInOut(board.D2)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# NeoPixel
pixels = neopixel.NeoPixel(board.D3, 1, brightness=0.2)

# ================= 3. 辅助函数 =================

def show_screen(line1="", line2="", line3="", scale1=1, scale2=1, scale3=1):
    """
    显示三行文字，可分别指定大小
    """
    while len(main_group) > 0:
        main_group.pop()
    
    # 第一行 (标题) - 顶部
    if line1:
        text_area1 = label.Label(terminalio.FONT, text=line1, color=0xFFFFFF, scale=scale1)
        text_area1.anchor_point = (0.5, 0.0) 
        text_area1.anchored_position = (64, 0)
        main_group.append(text_area1)
    
    # 第二行 (中间) - 正中心
    if line2:
        text_area2 = label.Label(terminalio.FONT, text=line2, color=0xFFFFFF, scale=scale2)
        text_area2.anchor_point = (0.5, 0.5) 
        text_area2.anchored_position = (64, 32)
        main_group.append(text_area2)
        
    # 第三行 (底部) - 底部
    if line3:
        text_area3 = label.Label(terminalio.FONT, text=line3, color=0xFFFFFF, scale=scale3)
        text_area3.anchor_point = (0.5, 1.0) 
        text_area3.anchored_position = (64, 60) # 留一点边距
        main_group.append(text_area3)

def set_color(color):
    pixels.fill(color)
    pixels.show()

def get_tilt():
    if not accel: return "NONE"
    try:
        x, y, z = accel.acceleration
        th = 6.0
        if abs(x) > abs(y): return "LEFT" if x > th else "RIGHT" if x < -th else "NONE"
        else: return "BACK" if y > th else "FORWARD" if y < -th else "NONE"
    except:
        return "NONE"

def wait_btn(press=True):
    target = not press
    while button.value == target:
        encoder.update()
    time.sleep(0.1)

# ================= 4. 游戏逻辑 =================

MOVES = ["LEFT", "RIGHT", "FORWARD", "BACK", "TWIST"]
DIFFS = ["EASY", "MED", "HARD", "DIFF+"]
TIMES = [3.0, 2.2, 1.5, 0.8]
current_diff = 0

def menu():
    global current_diff, last_pos_global
    set_color((0, 0, 255))
    
    # 【修改】：标题大小改为 1 (原来是2)，选项大小保持 2 (醒目)
    show_screen("COSMIC TILT", f"< {DIFFS[current_diff]} >", "PRESS TO START", 1, 2, 1)
    
    enc_acc = 0
    
    while True:
        encoder.update()
        curr = encoder.pos
        diff = curr - last_pos_global
        last_pos_global = curr
        enc_acc += diff
        
        # 旋钮防抖：每4格动一次
        if abs(enc_acc) >= 4:
            direction = 1 if enc_acc > 0 else -1
            current_diff = (current_diff + direction) % 4
            enc_acc = 0
            # 刷新屏幕
            show_screen("COSMIC TILT", f"< {DIFFS[current_diff]} >", "PRESS TO START", 1, 2, 1)
            
        if not button.value:
            wait_btn(False)
            return

def game():
    level = 1
    score = 0
    time_limit = TIMES[current_diff]
    
    # 倒计时
    for i in range(3, 0, -1):
        show_screen("", str(i), "", 1, 4, 1)
        set_color((255, 255, 0))
        time.sleep(0.5)
        set_color((0, 0, 0))
        time.sleep(0.5)
        
    playing = True
    while playing:
        limit = max(0.5, time_limit - (level-1)*0.08)
        target = random.choice(MOVES)
        
        # 游戏中显示：Level (小), Target (大)
        show_screen(f"LEVEL {level}", target, "", 1, 2, 1)
        set_color((255, 255, 255))
        
        start_t = time.monotonic()
        success = False
        
        encoder.update()
        start_enc = encoder.pos
        
        while time.monotonic() - start_t < limit:
            encoder.update()
            
            if target == "TWIST" and abs(encoder.pos - start_enc) > 4:
                success = True; break
            
            if target != "TWIST" and get_tilt() == target:
                success = True; break
        
        if success:
            set_color((0, 255, 0))
            score += 100
            level += 1
            time.sleep(0.3)
            if level > 10:
                win(score); return
        else:
            fail(score); return

def fail(s):
    set_color((255, 0, 0))
    # 【修改】：GAME OVER 改为大小 1
    show_screen("GAME OVER", f"SCORE: {s}", "PRESS TO RESET", 1, 2, 1)
    wait_btn(True); wait_btn(False)

def win(s):
    # 【修改】：YOU WIN 改为大小 1
    show_screen("YOU WIN!", f"SCORE: {s}", "PRESS TO RESET", 1, 2, 1)
    while button.value:
        encoder.update()
        for i in range(10):
            pixels[0] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
            time.sleep(0.05)
            if not button.value: break
    wait_btn(False)

# ================= 主循环 =================
if not accel:
    show_screen("ERROR", "ADXL MISSING", "CHECK WIRING", 2, 1, 1)
    while True: pass

while True:
    menu()
    game()