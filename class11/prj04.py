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
        # 新增屬性: 記錄目前面向方向 ("M"=直飛, "L"=左, "R"=右)
        self.facing_direction = "M"
        # 火焰推進相關屬性
        self.burner_img = sprites["burner"] if sprites and "burner" in sprites else None
        self.burn_shift = 0  # 火焰動畫位移(循環)

    def draw(self, screen):
        """
        在螢幕上繪製太空船，先繪製火焰推進，再繪製太空船本體
        """
        # 先繪製火焰推進效果
        if self.burner_img and not keys[K_DOWN]:
            # 火焰寬度為太空船寬度的1/4，高度等比例縮放
            burner_w = self.rect.width // 4
            burner_h = int(
                self.burner_img.get_height() * (burner_w / self.burner_img.get_width())
            )
            # 火焰動畫上下晃動(循環0~11)
            self.burn_shift = (self.burn_shift + 2) % 12
            # 火焰中心對齊太空船底部中央，並有微小上下位移
            burner_x = self.rect.centerx - burner_w // 2
            burner_y = self.rect.bottom - burner_h // 2 + self.burn_shift - 6
            burner_img_scaled = pygame.transform.scale(
                self.burner_img, (burner_w, burner_h)
            )
            screen.blit(burner_img_scaled, (burner_x, burner_y))
        # 再繪製太空船本體
        if self.sprites:
            # 根據方向選擇圖片
            key = f"fighter_{self.facing_direction}"
            if key in self.sprites:
                img = pygame.transform.scale(
                    self.sprites[key], (self.rect.width, self.rect.height)
                )
                screen.blit(img, self.rect)
                return
        # 沒有圖片時畫矩形
        pygame.draw.rect(screen, self.color, self.rect)

    def handle_input(self, keys, bg_x, bg_y):
        """
        處理玩家輸入與移動，並自動邊界檢查(融合)
        keys: 按鍵狀態
        bg_x, bg_y: 視窗寬高
        """
        # 預設方向為直飛
        self.facing_direction = "M"
        # 左移
        if keys[K_LEFT] and self.rect.left - self.speed >= 0:
            self.rect.x -= self.speed
            self.facing_direction = "L"  # 按左鍵顯示左轉
        # 右移
        if keys[K_RIGHT] and self.rect.right + self.speed <= bg_x:
            self.rect.x += self.speed
            self.facing_direction = "R"  # 按右鍵顯示右轉
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
# 載入太空船左轉圖片
img_player_l = pygame.image.load(os.path.join("image", "fighter_L.png"))
# 載入太空船右轉圖片
img_player_r = pygame.image.load(os.path.join("image", "fighter_R.png"))
# 載入火焰推進圖片
img_burner = pygame.image.load(os.path.join("image", "starship_burner.png"))
# 建立太空船圖片字典，三種狀態
player_sprites = {
    "fighter_M": img_player_m,  # 直飛
    "fighter_L": img_player_l,  # 左轉
    "fighter_R": img_player_r,  # 右轉
    "burner": img_burner,  # 火焰推進
}

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
# 建立玩家物件，sprites已包含火焰推進圖片
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
