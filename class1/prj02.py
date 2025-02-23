######################匯入模組######################
import pygame as g  # 在終端機輸入 pip install pygame -U
import sys
import math

######################初始化######################
g.init()  # 啟動 Pygame
width = 640  # 設定視窗寬度
height = 320  # 設定視窗高度


######################建立視窗及物件######################
# 設定視窗大小
screen = g.display.set_mode((width, height))
# 設定視窗標題
g.display.set_caption("Pygame")
#####################建立畫布######################
# 建立畫布
bg = g.Surface((width, height))
# 畫布為白色(R，G，B)
bg.fill((255, 255, 255))
######################畫圖######################
# 畫圓形，(畫布，顏色，圓心，半徑，線寬)
g.draw.circle(bg, (0, 0, 255), (320, 160), 50, 0)

# 畫矩形，(畫布，顏色，(X座標，Y座標，寬，高)，線寬)
g.draw.rect(bg, (0, 255, 0), (100, 100, 100, 100), 0)

# 畫橢圓形，(畫布，顏色，(X座標，Y座標，寬，高)，線寬)
g.draw.ellipse(bg, (255, 0, 0), (400, 100, 100, 50), 0)

# 畫弧形，(畫布，顏色，(X座標，Y座標，寬，高)，起始角度，結束角度，線寬)
g.draw.arc(bg, (0, 0, 0), (100, 200, 100, 100), math.radians(0), math.radians(90), 1)

# 畫多邊形，(畫布，顏色，[(X座標1，Y座標1)，(X座標2，Y座標2)，(X座標3，Y座標3)，...，(X座標n，Y座標n)]，線寬)
g.draw.polygon(bg, (255, 0, 255), [(400, 200), (500, 200), (450, 250)], 0)

# 畫直線，(畫布，顏色，(起點X座標，起點Y座標)，(終點X座標，終點Y座標)，線寬)
g.draw.line(bg, (0, 0, 0), (0, 0), (640, 320), 1)

######################循環偵測######################
while True:
    x, y = g.mouse.get_pos()  # 取得滑鼠座標
    for event in g.event.get():
        if event.type == g.QUIT:  # 如果按下[X]按鈕就退出
            sys.exit()  # 離開遊戲
        if event.type == g.MOUSEBUTTONDOWN:
            print("滑鼠按下")
            print("滑鼠座標:", x, y)
    screen.blit(
        bg, (0, 0)
    )  # 以左上角為起點，橫線為X座標，直線為Y座標，前面寫的是X座標，後面寫的是Y座標

    g.display.update()  # 更新視窗
