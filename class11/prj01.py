# #################### 載入套件 ####################
import pygame  # 載入 pygame 套件，用於遊戲開發
import sys  # 載入 sys 套件，處理系統相關操作
import os  # 載入 os 套件，處理檔案路徑
from pygame.locals import *  # 載入 pygame 常用常數


# #################### 定義函式 ####################
def roll_bg(screen, bg_img, roll_y):
    """
    捲動背景圖片
    screen: 遊戲視窗
    bg_img: 背景圖片
    roll_y: 當前捲動的Y座標
    """
    bg_y = bg_img.get_height()
    # 先畫上半部
    screen.blit(bg_img, (0, roll_y - bg_y))
    # 再畫下半部
    screen.blit(bg_img, (0, roll_y))


# #################### 初始化設定 ####################
os.chdir(sys.path[0])  # 設定工作目錄為程式所在位置
pygame.init()  # 初始化 pygame
clock = pygame.time.Clock()  # 建立時鐘物件控制遊戲速度

# #################### 載入圖片 ####################
# 載入太空背景圖片
bg_img = pygame.image.load(os.path.join("image", "space.png"))

# #################### 遊戲視窗設定 ####################
bg_x = bg_img.get_width()  # 取得背景圖片寬度
bg_y = bg_img.get_height()  # 取得背景圖片高度
screen = pygame.display.set_mode((bg_x, bg_y))  # 設定遊戲視窗大小
pygame.display.set_caption("Galaxy Lancer")  # 設定視窗標題
roll_y = 0  # 捲動背景的Y座標

# #################### 主程式 ####################
while True:
    clock.tick(60)  # 控制遊戲迴圈速度為每秒60幀
    roll_y = (roll_y + 10) % bg_y  # 每次捲動10像素，並循環
    roll_bg(screen, bg_img, roll_y)  # 繪製捲動背景

    # 處理事件
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()  # 關閉視窗時結束程式
        elif event.type == KEYDOWN:
            if event.key == K_F1:
                # 切換全螢幕
                screen = pygame.display.set_mode((bg_x, bg_y), FULLSCREEN)
            elif event.key == K_ESCAPE:
                # 返回視窗模式
                screen = pygame.display.set_mode((bg_x, bg_y))

    pygame.display.update()  # 更新畫面顯示
