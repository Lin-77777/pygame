# 這段程式碼是用來建立一個簡單的畫圖工具，使用者可以在視窗中點擊並拖動滑鼠來畫出藍色的線。。
######################匯入模組######################
import pygame as g  # 在終端機輸入 pip install pygame -U
import sys

######################初始化######################
g.init()  # 啟動 Pygame
width = 1000  # 設定視窗寬度
height = 600  # 設定視窗高度
######################建立視窗及物件######################
# 設定視窗大小
screen = g.display.set_mode((width, height))
# 設定視窗標題
g.display.set_caption("畫圖工具")
#####################建立畫布######################
# 建立畫布
bg = g.Surface((width, height))
# 畫布為白色(R，G，B)
bg.fill((255, 255, 255))
paint = False
######################循環偵測######################
while True:
    x, y = g.mouse.get_pos()  # 取得滑鼠座標

    for event in g.event.get():
        if event.type == g.QUIT:  # 如果按下[X]按鈕就退出
            sys.exit()  # 離開遊戲
        if event.type == g.MOUSEBUTTONDOWN:
            paint = not (paint)
    if paint:  # 因為直接是真假所以不用等於
        g.draw.circle(bg, (0, 0, 255), (x, y), 10, 0)
    screen.blit(
        bg, (0, 0)
    )  # 以左上角為起點，橫線為X座標，直線為Y座標，前面寫的是X座標，後面寫的是Y座標
    g.display.update()  # 更新視窗
