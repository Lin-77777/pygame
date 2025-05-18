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


# #################### 玩家類別 ####################
class Player:
    def __init__(self, x, y, width, height, color, sprites=None):
        """
        初始化玩家太空船
        x, y: 太空船左上角座標
        width, height: 太空船寬高
        color: 預設顏色 (無圖片時使用)
        sprites: 太空船圖片字典
        """
        self.rect = pygame.Rect(x, y, width, height)  # 太空船矩形區域
        self.color = color  # 預設顏色
        self.sprites = sprites  # 圖片字典
        self.speed = 10  # 移動速度(每次移動10像素)

    def draw(self, screen):
        """
        在螢幕上繪製太空船
        """
        if self.sprites and "fighter_M" in self.sprites:
            # 若有圖片則繪製圖片
            img = pygame.transform.scale(
                self.sprites["fighter_M"], (self.rect.width, self.rect.height)
            )
            screen.blit(img, self.rect)
        else:
            # 沒有圖片時畫矩形
            pygame.draw.rect(screen, self.color, self.rect)

    def handle_input(self, keys, bg_x, bg_y):
        """
        處理玩家輸入與移動，並自動邊界檢查(融合)
        keys: 按鍵狀態
        bg_x, bg_y: 視窗寬高
        """
        # 左移
        if keys[K_LEFT] and self.rect.left - self.speed >= 0:
            self.rect.x -= self.speed
        # 右移
        if keys[K_RIGHT] and self.rect.right + self.speed <= bg_x:
            self.rect.x += self.speed
        # 上移
        if keys[K_UP] and self.rect.top - self.speed >= 0:
            self.rect.y -= self.speed
        # 下移
        if keys[K_DOWN] and self.rect.bottom + self.speed <= bg_y:
            self.rect.y += self.speed


# #################### 初始化設定 ####################
os.chdir(sys.path[0])  # 設定工作目錄為程式所在位置
pygame.init()  # 初始化 pygame
clock = pygame.time.Clock()  # 建立時鐘物件控制遊戲速度

# #################### 載入圖片 ####################
# 載入太空背景圖片
bg_img = pygame.image.load(os.path.join("image", "space.png"))
# 載入太空船圖片(中間直飛)
img_player_m = pygame.image.load(os.path.join("image", "fighter_M.png"))
# 建立太空船圖片字典
player_sprites = {"fighter_M": img_player_m}

# #################### 遊戲視窗設定 ####################
bg_x = bg_img.get_width()  # 取得背景圖片寬度
bg_y = bg_img.get_height()  # 取得背景圖片高度
screen = pygame.display.set_mode((bg_x, bg_y))  # 設定遊戲視窗大小
pygame.display.set_caption("Galaxy Lancer")  # 設定視窗標題
roll_y = 0  # 捲動背景的Y座標

# #################### 玩家設定 ####################
player_w, player_h = 60, 60  # 太空船尺寸
player_x = (bg_x - player_w) // 2  # 初始X(置中)
player_y = (bg_y - player_h) // 2  # 初始Y(置中)
# 建立玩家物件
player = Player(player_x, player_y, player_w, player_h, (0, 255, 0), player_sprites)

# #################### 主程式 ####################
while True:
    clock.tick(60)  # 控制遊戲迴圈速度為每秒60幀
    roll_y = (roll_y + 10) % bg_y  # 每次捲動10像素，並循環
    roll_bg(screen, bg_img, roll_y)  # 繪製捲動背景

    # 取得按鍵狀態並交由玩家物件處理
    keys = pygame.key.get_pressed()
    player.handle_input(keys, bg_x, bg_y)

    # 繪製玩家太空船
    player.draw(screen)

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
