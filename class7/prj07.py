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
        self.score = 0  # 玩家得分
        self.is_dead = False  # 玩家是否死亡

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
        if self.is_dead:  # 如果玩家死亡，不處理移動
            return

        # 根據方向和速度移動
        self.rect.x += direction * self.speed

        # 實現穿牆效果
        if self.rect.right < 0:  # 完全超出左邊界時
            self.rect.left = bg_x  # 從右邊出現
        elif self.rect.left > bg_x:  # 完全超出右邊界時
            self.rect.right = 0  # 從左邊出現

    def update(self, camera_y, bg_y):
        """
        更新主角的垂直位置和狀態\n
        camera_y: 當前攝影機的垂直位置\n
        bg_y: 遊戲視窗高度\n
        """
        if self.is_dead:  # 如果玩家死亡，不更新位置
            return

        self.jump_speed += self.gravity  # 加入重力效果
        self.rect.y += self.jump_speed  # 更新垂直位置
        # 更新最高點記錄
        if self.rect.y < self.highest_y:
            self.highest_y = self.rect.y

        # 檢查是否掉出畫面（死亡判定）
        if self.rect.y - camera_y > bg_y + 100:
            self.is_dead = True

    def jump(self):
        """觸發主角的跳躍動作"""
        if not self.is_dead:  # 只有在活著時才能跳躍
            self.jump_speed = self.jump_power


class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (255, 255, 255)  # 平台顏色設定為白色
        self.is_scored = False  # 追蹤是否已經在這個平台得過分

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
        if player.is_dead:  # 如果玩家已死亡，不檢查碰撞
            return False

        # 只在玩家下落時檢查碰撞
        if player.jump_speed > 0:  # 玩家正在下落
            if self.rect.colliderect(player.rect):  # 檢查碰撞
                if player.rect.bottom >= self.rect.top:
                    player.rect.bottom = self.rect.top  # 將玩家位置調整到平台上
                    if not self.is_scored:  # 如果這個平台還沒得過分
                        player.score += 10  # 加10分
                        self.is_scored = True  # 標記這個平台已經得過分
                    player.jump()  # 觸發跳躍
                    return True
        return False


######################文字顯示相關函式######################
def draw_text(screen, text, size, x, y, color=(255, 255, 255)):
    """
    在畫面上顯示文字\n
    screen: 遊戲畫面\n
    text: 要顯示的文字\n
    size: 文字大小\n
    x,y: 文字位置\n
    color: 文字顏色，預設白色\n
    """
    font = pygame.font.Font("C:/Windows/Fonts/msjh.ttc", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.x = x
    text_rect.y = y
    screen.blit(text_surface, text_rect)


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
# 遊戲主迴圈
while True:
    FPS.tick(60)  # 設定FPS為60
    screen.fill((0, 0, 0))  # 設定背景為黑色

    # 事件處理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 關閉視窗事件
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:  # 按鍵按下事件
            if event.key == pygame.K_r and player.is_dead:  # 按R鍵重新開始遊戲
                # 重置遊戲狀態
                player.is_dead = False
                player.score = 0
                player.highest_y = player.rect.y = bg_y - player_h - 50
                player.rect.x = bg_x // 2 - player_w // 2
                player.jump_speed = 0
                camera_y = 0
                create_starting_platforms()

    # 取得按鍵狀態
    keys = pygame.key.get_pressed()
    # 處理左右移動
    if keys[pygame.K_LEFT]:  # 按下左方向鍵
        player.move(-1, bg_x)
    if keys[pygame.K_RIGHT]:  # 按下右方向鍵
        player.move(1, bg_x)

    # 更新遊戲狀態
    player.update(camera_y, bg_y)  # 更新主角位置
    if not player.is_dead:  # 只在玩家活著時更新攝影機
        # 更新攝影機位置
        target_camera_y = player.rect.y - (bg_y * 0.7)  # 保持主角在畫面下方30%處
        new_camera_y = camera_y + (target_camera_y - camera_y) * camera_speed
        if new_camera_y < camera_y:  # 相機只能向上移動，不能向下移動
            camera_y = new_camera_y

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

    # 顯示分數
    draw_text(screen, f"分數: {player.score}", 30, 10, 10)

    # 如果遊戲結束，顯示重新開始提示
    if player.is_dead:
        draw_text(screen, "遊戲結束！", 40, bg_x // 2 - 80, bg_y // 2 - 50)
        draw_text(screen, f"最終分數: {player.score}", 30, bg_x // 2 - 70, bg_y // 2)
        draw_text(screen, "按R鍵重新開始", 25, bg_x // 2 - 60, bg_y // 2 + 40)

    # 更新畫面
    pygame.display.update()
