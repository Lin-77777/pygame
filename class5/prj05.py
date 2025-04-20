######################載入套件######################
import pygame
import sys
import random as r


######################物件類別######################
class Player:
    def __init__(self, x, y, width, height):
        """
        初始化主角\n
        x,y: 主角的左上角座標\n
        width,height: 主角的寬度與高度\n
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (0, 255, 0)  # 主角顏色設定為綠色
        self.speed = 5  # 主角的水平移動速度
        self.jump_speed = 0  # 主角的垂直速度，初始為0
        self.gravity = 0.5  # 重力加速度，影響下落速度
        self.jump_power = -10  # 跳躍初始速度 (負值代表向上)

    def draw(self, display_area):
        """
        繪製主角於畫面上\n
        display_area: 遊戲顯示區域\n
        """
        pygame.draw.rect(display_area, self.color, self.rect)

    def move(self, direction, bg_x):
        """
        處理主角的水平移動\n
        direction: 移動方向 (-1 是向左, 1 是向右)\n
        bg_x: 遊戲視窗寬度，用於檢查邊界\n
        """
        # 根據方向和速度移動
        self.rect.x += direction * self.speed

        # 實現穿牆效果
        if self.rect.right < 0:  # 完全超出左邊界時
            self.rect.left = bg_x  # 從右邊出現
        elif self.rect.left > bg_x:  # 完全超出右邊界時
            self.rect.right = 0  # 從左邊出現

    def update(self):
        """
        更新主角的垂直位置\n
        包含重力效果的計算\n
        """
        self.jump_speed += self.gravity  # 加入重力效果
        self.rect.y += self.jump_speed  # 更新垂直位置

    def jump(self):
        """
        觸發主角的跳躍動作\n
        """
        self.jump_speed = self.jump_power  # 設定向上的初始跳躍速度


class Platform:
    def __init__(self, x, y, width, height):
        """
        初始化平台\n
        x,y: 平台的左上角座標\n
        width,height: 平台的寬度與高度\n
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (255, 255, 255)  # 平台顏色設定為白色

    def draw(self, display_area):
        """
        繪製平台於畫面上\n
        display_area: 遊戲顯示區域\n
        """
        pygame.draw.rect(display_area, self.color, self.rect)

    def check_collision(self, player):
        """
        檢查平台與玩家的碰撞\n
        player: 玩家物件\n
        return: 布林值，表示是否發生碰撞\n
        """
        # 只在玩家下落時檢查碰撞
        if player.jump_speed > 0:  # 玩家正在下落
            if self.rect.colliderect(player.rect):  # 檢查碰撞
                # 確認是從平台上方碰撞
                if player.rect.bottom >= self.rect.top:
                    player.rect.bottom = self.rect.top  # 將玩家位置調整到平台上
                    player.jump()  # 觸發跳躍
                    return True
        return False


######################初始化設定######################
pygame.init()  # 初始化pygame
FPS = pygame.time.Clock()  # 設定FPS時鐘

######################遊戲視窗設定######################
bg_x = 400  # 視窗寬度
bg_y = 600  # 視窗高度
bg_size = (bg_x, bg_y)  # 視窗大小
pygame.display.set_caption("Doodle Jump")  # 設定視窗標題
screen = pygame.display.set_mode(bg_size)  # 建立視窗

######################主角設定######################
player_w = 30  # 主角寬度
player_h = 30  # 主角高度
# 設定主角初始位置在視窗底部中間
player = Player(bg_x // 2 - player_w // 2, bg_y - player_h - 50, player_w, player_h)

######################平台設定######################
platform_w = 60  # 平台寬度
platform_h = 10  # 平台高度
platforms = []  # 平台列表

# 設定平台數量（包含初始平台）
platform_count = r.randint(8, 10)  # 隨機生成8-10個平台
min_platform_spacing = 60  # 平台最小間距

# 計算平台的垂直分布範圍
available_height = bg_y - 100  # 保留上下邊界的空間
max_spacing = available_height // (platform_count - 1)  # 最大間距

for i in range(platform_count):
    if i == 0:  # 第一個平台作為初始平台
        x = bg_x // 2 - platform_w // 2  # X座標置中
        y = bg_y - player_h - 20  # Y座標在主角下方
    else:
        # 隨機產生平台的x座標，確保不會太靠近邊緣
        x = r.randint(20, bg_x - platform_w - 20)
        # 計算平台的y座標，確保間距適中
        base_y = bg_y - i * (available_height // (platform_count - 1))
        y = base_y + r.randint(-10, 10)  # 加入一些隨機變化

    # 確保y座標不會太接近其他平台
    if i > 0:
        prev_platform = platforms[-1]
        min_y = prev_platform.rect.y - max_spacing
        if y > min_y:
            y = min_y

    # 建立新平台並加入列表
    platform = Platform(x, y, platform_w, platform_h)
    platforms.append(platform)

######################主程式######################
while True:
    FPS.tick(60)  # 設定FPS為60
    screen.fill((0, 0, 0))  # 設定背景為黑色

    # 事件處理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 關閉視窗事件
            pygame.quit()
            sys.exit()

    # 取得按鍵狀態
    keys = pygame.key.get_pressed()
    # 處理左右移動
    if keys[pygame.K_LEFT]:  # 按下左方向鍵
        player.move(-1, bg_x)
    if keys[pygame.K_RIGHT]:  # 按下右方向鍵
        player.move(1, bg_x)

    # 更新遊戲狀態
    player.update()  # 更新主角位置

    # 處理所有平台的碰撞檢測和繪製
    for platform in platforms:
        platform.draw(screen)  # 繪製平台
        platform.check_collision(player)  # 檢查碰撞

    # 繪製主角
    player.draw(screen)

    # 更新畫面
    pygame.display.update()
