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
        speed: 主角的水平移動速度\n
        jump_speed: 主角的垂直速度\n
        gravity: 重力加速度\n
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (0, 255, 0)  # 主角顏色為綠色
        self.speed = 5  # 主角的水平移動速度
        self.jump_speed = 0  # 主角的垂直速度
        self.gravity = 0.5  # 重力加速度
        self.jump_power = -10  # 跳躍初始速度 (負值表示向上)

    def draw(self, display_area):
        """
        畫出主角\n
        display_area: 繪製主角的區域\n
        """
        pygame.draw.rect(display_area, self.color, self.rect)

    def move(self, direction, bg_x):
        """
        水平移動主角\n
        direction: 移動方向 (-1 為左, 1 為右)\n
        bg_x: 遊戲視窗寬度，用於檢查邊界\n
        """
        self.rect.x += direction * self.speed  # 根據方向和速度移動

        # 檢查是否超出邊界，實現穿牆效果
        if self.rect.right < 0:  # 如果完全超出左邊界
            self.rect.left = bg_x  # 從右邊出現
        elif self.rect.left > bg_x:  # 如果完全超出右邊界
            self.rect.right = 0  # 從左邊出現

    def update(self):
        """
        更新主角的垂直位置\n
        加入重力效果使主角自動下落\n
        """
        # 更新垂直速度和位置
        self.jump_speed += self.gravity  # 重力加速度影響垂直速度
        self.rect.y += self.jump_speed  # 根據垂直速度更新位置

    def jump(self):
        """
        觸發主角跳躍\n
        """
        self.jump_speed = self.jump_power  # 設定向上的初始速度


class Platform:
    def __init__(self, x, y, width, height):
        """
        初始化平台\n
        x,y: 平台的左上角座標\n
        width,height: 平台的寬度與高度\n
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (255, 255, 255)  # 平台顏色為白色

    def draw(self, display_area):
        """
        繪製平台\n
        display_area: 繪製平台的區域\n
        """
        pygame.draw.rect(display_area, self.color, self.rect)

    def check_collision(self, player):
        """
        檢查與玩家的碰撞\n
        player: 玩家物件\n
        return: 是否發生碰撞\n
        """
        # 只在玩家往下落時檢查碰撞
        if player.jump_speed > 0:  # 如果玩家正在下降
            if self.rect.colliderect(player.rect):  # 如果發生碰撞
                if player.rect.bottom >= self.rect.top:  # 確保是從上方碰撞
                    player.rect.bottom = self.rect.top  # 將玩家位置調整到平台上
                    player.jump()  # 讓玩家跳躍
                    return True
        return False


######################初始化設定######################
pygame.init()  # 初始化pygame
FPS = pygame.time.Clock()  # 設定FPS

######################遊戲視窗設定######################
bg_x = 400  # 視窗寬度
bg_y = 600  # 視窗高度
bg_size = (bg_x, bg_y)  # 視窗大小
pygame.display.set_caption("Doodle Jump")  # 設定視窗標題
screen = pygame.display.set_mode(bg_size)  # 設定視窗大小

######################主角設定######################
player_w = 30  # 主角寬度
player_h = 30  # 主角高度
# 設定主角初始位置在視窗底部中間
player = Player(bg_x // 2 - player_w // 2, bg_y - player_h - 50, player_w, player_h)

######################平台設定######################
platform_w = 60  # 平台寬度
platform_h = 10  # 平台高度
platforms = []  # 平台列表

# 新增初始平台在玩家下方
initial_platform = Platform(bg_x // 2 - platform_w // 2, bg_y - player_h - 20, platform_w, platform_h)
platforms.append(initial_platform)

# 初始化靜態平台
platform_count = 8  # 平台數量
for i in range(platform_count):
    # 隨機產生平台的x座標
    x = r.randint(0, bg_x - platform_w)
    # 平均分配平台的y座標
    y = bg_y - (i + 1) * (bg_y // platform_count)
    platform = Platform(x, y, platform_w, platform_h)
    platforms.append(platform)

######################主程式######################
while True:
    FPS.tick(60)  # 設定FPS為60
    screen.fill((0, 0, 0))  # 設定背景為黑色

    # 事件處理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 點擊關閉視窗
            pygame.quit()
            sys.exit()

    # 取得按鍵狀態
    keys = pygame.key.get_pressed()
    # 檢查左右方向鍵是否被按下
    if keys[pygame.K_LEFT]:  # 按下左方向鍵
        player.move(-1, bg_x)  # 向左移動
    if keys[pygame.K_RIGHT]:  # 按下右方向鍵
        player.move(1, bg_x)  # 向右移動

    # 更新主角位置
    player.update()

    # 處理碰撞和繪製
    for platform in platforms:
        platform.draw(screen)  # 繪製平台
        platform.check_collision(player)  # 檢查碰撞並處理跳躍

    # 繪製主角
    player.draw(screen)

    # 更新畫面
    pygame.display.update()
