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
        self.highest_y = self.rect.y  # 記錄主角到達的最高點

    def draw(self, display_area, camera_y):
        """
        繪製主角於畫面上\n
        display_area: 遊戲顯示區域\n
        camera_y: 攝影機的垂直偏移量\n
        """
        # 根據攝影機位置調整繪製位置
        draw_rect = pygame.Rect(
            self.rect.x, self.rect.y - camera_y, self.rect.width, self.rect.height
        )
        pygame.draw.rect(display_area, self.color, draw_rect)

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

        # 更新最高點記錄
        if self.rect.y < self.highest_y:
            self.highest_y = self.rect.y

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

    def draw(self, display_area, camera_y):
        """
        繪製平台於畫面上\n
        display_area: 遊戲顯示區域\n
        camera_y: 攝影機的垂直偏移量\n
        """
        # 根據攝影機位置調整繪製位置
        draw_rect = pygame.Rect(
            self.rect.x, self.rect.y - camera_y, self.rect.width, self.rect.height
        )
        pygame.draw.rect(display_area, self.color, draw_rect)

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
min_platform_spacing = 60  # 平台最小間距


# 初始平台設置
def create_starting_platforms():
    """建立初始平台"""
    platforms.clear()  # 清空現有平台

    # 設定平台數量
    platform_count = r.randint(8, 10)

    # 計算平台的垂直分布範圍
    available_height = bg_y - 100
    max_spacing = available_height // (platform_count - 1)

    def check_initial_overlap(new_x, new_y, current_platforms):
        """檢查初始平台是否與已存在的平台重疊"""
        new_rect = pygame.Rect(new_x, new_y, platform_w, platform_h)
        for platform in current_platforms:
            if (
                abs(platform.rect.x - new_x) < platform_w
                and abs(platform.rect.y - new_y) < min_platform_spacing
            ):
                return True
        return False

    for i in range(platform_count):
        if i == 0:  # 第一個平台作為初始平台
            x = bg_x // 2 - platform_w // 2
            y = bg_y - player_h - 20
        else:
            # 嘗試生成不重疊的平台，最多嘗試10次
            for _ in range(10):
                x = r.randint(20, bg_x - platform_w - 20)
                base_y = bg_y - i * (available_height // (platform_count - 1))
                y = base_y + r.randint(-10, 10)
                if not check_initial_overlap(x, y, platforms):
                    break

        platform = Platform(x, y, platform_w, platform_h)
        platforms.append(platform)


def create_new_platform(min_y):
    """
    在上方生成新的平台\n
    min_y: 新平台的最小高度\n
    """

    def check_overlap(new_x, new_y):
        """檢查新平台是否與現有平台重疊"""
        new_rect = pygame.Rect(new_x, new_y, platform_w, platform_h)
        for platform in platforms:
            # 檢查水平和垂直方向的距離
            if (
                abs(platform.rect.x - new_x) < platform_w
                and abs(platform.rect.y - new_y) < min_platform_spacing
            ):
                return True
        return False

    # 嘗試生成不重疊的平台，最多嘗試10次
    for _ in range(10):
        x = r.randint(20, bg_x - platform_w - 20)
        y = min_y - r.randint(50, 80)
        if not check_overlap(x, y):
            return Platform(x, y, platform_w, platform_h)

    # 如果10次都無法找到合適位置，則直接返回
    return Platform(x, y, platform_w, platform_h)


# 建立初始平台
create_starting_platforms()

######################攝影機設定######################
camera_y = 0  # 攝影機垂直偏移量
target_camera_y = 0  # 目標攝影機位置
camera_speed = 0.1  # 攝影機跟隨速度

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

    # 更新攝影機位置
    target_camera_y = player.rect.y - (bg_y * 0.7)  # 保持主角在畫面下方30%處
    camera_y += (target_camera_y - camera_y) * camera_speed

    # 刪除離開視窗底部的平台
    new_platforms = []
    for p in platforms:
        if p.rect.y - camera_y < bg_y + 100:
            new_platforms.append(p)
    platforms = new_platforms
    # 在頂部生成新平台
    if len(platforms) > 0:
        highest_platform = min(platforms, key=lambda p: p.rect.y)
        if highest_platform.rect.y > player.highest_y - 200:
            platforms.append(create_new_platform(highest_platform.rect.y))

    # 處理所有平台的碰撞檢測和繪製
    for platform in platforms:
        platform.draw(screen, camera_y)  # 繪製平台
        platform.check_collision(player)  # 檢查碰撞

    # 繪製主角
    player.draw(screen, camera_y)

    # 更新畫面
    pygame.display.update()
