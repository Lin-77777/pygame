######################載入套件######################
import pygame  # 載入 pygame 套件，用於遊戲開發
import sys  # 載入 sys 套件，用於系統相關操作
import os  # 載入 os 套件，用於處理檔案路徑
import random  # 載入 random 套件，用於隨機生成平台

os.chdir(sys.path[0])  # 設定當前工作目錄為程式所在位置


######################載入圖片######################
def load_doodle_sprites():
    """
    載入遊戲所需的圖片資源\n
    從source圖片切割各種平台和彈簧精靈\n
    載入玩家角色四個方向的圖片\n
    return: 包含所有精靈的字典\n
    """
    # 載入主要圖片資源
    img_path = os.path.join("image", "src.png")
    source_image = pygame.image.load(
        img_path
    ).convert_alpha()  # 載入圖片並轉換為帶Alpha通道的格式    # 定義精靈在原始圖片中的座標和尺寸
    sprite_data = {
        # 各種平台的座標和尺寸 (x, y, 寬, 高)
        "std_platform": (0, 0, 116, 30),  # 標準平台
        "break_platform": (0, 145, 124, 33),  # 可破壞平台
        # 道具精靈
        "spring_normal": (376, 188, 71, 35),  # 普通彈簧
        "propeller": (660, 473, 63, 40),  # 飛行帽
        # 玩家角色圖片路徑
        "player_left_jumping": os.path.join("image", "l.png"),  # 左跳躍
        "player_left_falling": os.path.join("image", "ls.png"),  # 左下落
        "player_right_jumping": os.path.join("image", "r.png"),  # 右跳躍
        "player_right_falling": os.path.join("image", "rs.png"),  # 右下落
    }

    # 切割精靈圖片並存入字典
    sprites = {}
    for name, data in sprite_data.items():
        if name.startswith("player_"):
            # 直接從檔案載入玩家角色圖片
            try:
                sprites[name] = pygame.image.load(data).convert_alpha()
            except Exception as e:
                print(f"無法載入玩家圖片 {name}: {e}")
        else:
            try:
                # 從主圖片切割出所需的精靈
                x, y, width, height = data  # 解包四個值
                sprites[name] = source_image.subsurface(
                    pygame.Rect(x, y, width, height)
                )
            except ValueError as e:
                print(f"無法切割 {name}: {e}")  # 如果切割失敗，輸出錯誤訊息

    return sprites  # 返回包含所有精靈的字典


######################全域變數######################
score = 0  # 紀錄當前分數
highest_score = 0  # 紀錄最高分數
game_over = False  # 紀錄遊戲是否結束
initial_player_y = 0  # 紀錄玩家的初始高度，用於計算分數


######################物件類別######################
class Player:
    def __init__(self, x, y, width, height, color, sprites=None):
        """
        初始化主角\n
        x, y: 主角的左上角座標\n
        width, height: 主角的寬度和高度\n
        color: 主角的顏色 (RGB格式)\n
        sprites: 精靈圖片字典\n
        """
        self.rect = pygame.Rect(x, y, width, height)  # 建立主角的矩形區域
        self.color = color  # 主角顏色(當沒有圖片時使用)
        self.sprites = sprites  # 精靈圖片字典
        self.speed = 5  # 水平移動速度
        self.velocity_y = 0  # 垂直速度
        self.jump_power = -12  # 跳躍初始力量（負值表示向上）
        self.gravity = 0.5  # 重力加速度
        self.on_platform = False  # 是否站在平台上
        self.facing_right = True  # 是否面向右方
        self.jumping = False  # 是否正在跳躍
        self.flying = False  # 是否正在飛行狀態
        self.fly_speed = -6.25  # 飛行時的上升速度（每幀-6.25像素）
        self.current_propeller = None  # 當前使用的飛行帽
        self.fly_time = 0  # 飛行時間計數器
        self.max_fly_time = 320  # 最大飛行時間（約8秒）

    def draw(self, display_area):
        """
        繪製主角\n
        display_area: 繪製主角的目標視窗\n
        """

        # 繪製主角
        if self.sprites:
            direction = "right" if self.facing_right else "left"
            state = "jumping" if self.velocity_y < 0 else "falling"
            sprite_key = f"player_{direction}_{state}"
            if sprite_key in self.sprites:
                sprite = self.sprites[sprite_key]
                scaled_sprite = pygame.transform.scale(
                    sprite, (self.rect.width, self.rect.height)
                )
                display_area.blit(scaled_sprite, self.rect)
            else:
                pygame.draw.rect(display_area, self.color, self.rect)
        else:
            pygame.draw.rect(display_area, self.color, self.rect)

        # 如果在飛行狀態，先繪製飛行帽
        if self.flying and self.sprites and "propeller" in self.sprites:
            propeller_sprite = self.sprites["propeller"]
            # 調整飛行帽大小為角色寬度，高度為寬度的一半，並稍微蓋住頭頂
            propeller_width = self.rect.width * 0.8
            propeller_height = int(self.rect.width * 0.5)
            scaled_propeller = pygame.transform.scale(
                propeller_sprite, (propeller_width, propeller_height)
            )
            # 將飛行帽放在主角頭頂，稍微蓋住頭部
            propeller_rect = scaled_propeller.get_rect()
            propeller_rect.centerx = self.rect.centerx
            propeller_rect.bottom = self.rect.top + 25  # 調整飛行帽位置
            display_area.blit(scaled_propeller, propeller_rect)

    def move(self, direction, bg_x):
        """
        移動主角並處理穿牆效果\n
        direction: 移動方向 (1為右移, -1為左移)\n
        bg_x: 遊戲視窗寬度，用於計算穿牆位置\n
        """
        # 根據方向和速度移動主角
        self.rect.x += direction * self.speed
        # 更新面向方向
        self.facing_right = direction > 0
        # 穿牆功能處理
        if self.rect.right < 0:  # 當主角完全移出左邊界時
            self.rect.left = bg_x  # 從右側重新出現
        elif self.rect.left > bg_x:  # 當主角完全移出右邊界時
            self.rect.right = 0  # 從左側重新出現

    def apply_gravity(self):
        """
        應用重力效果\n
        更新垂直速度和位置\n
        """
        if self.flying:  # 飛行狀態下保持固定上升速度
            self.velocity_y = self.fly_speed
        else:  # 一般狀態下應用重力
            self.velocity_y += self.gravity

        self.rect.y += self.velocity_y  # 更新垂直位置
        self.jumping = self.velocity_y < 0  # 更新跳躍狀態

    def check_platform_collision(self, platforms, propellers):
        """
        檢查與所有平台和道具的碰撞\n
        platforms: 要檢查碰撞的平台物件列表\n
        propellers: 要檢查碰撞的飛行帽列表\n
        """
        # 檢查與飛行帽的碰撞或更新飛行狀態
        if self.flying:  # 如果正在飛行中
            self.fly_time += 1
            # 飛行時播放飛行帽音效
            if propeller_sound:
                propeller_sound.play()
            # 當飛行時間結束
            if self.fly_time >= self.max_fly_time:
                self.flying = False
                self.velocity_y = 0  # 重置速度，讓玩家平滑降落
                self.current_propeller = None
                self.fly_time = 0
            return True
        else:  # 檢查新的飛行帽碰撞
            for propeller in propellers:
                if not propeller.active and self.rect.colliderect(propeller.rect):
                    self.flying = True
                    self.velocity_y = self.fly_speed
                    propeller.active = True
                    self.current_propeller = propeller
                    self.fly_time = 0
                    # 播放飛行帽音效
                    if propeller_sound:
                        propeller_sound.play()
                    return True

        # 只在玩家往下掉的時候檢查碰撞
        if self.velocity_y > 0 and not self.flying:
            # 計算檢測點數量，根據垂直速度決定檢測點的數量
            check_points = max(1, int(abs(self.velocity_y) / 5))
            step_y = self.velocity_y / check_points

            for platform in platforms:
                # 跳過已消失的特殊平台
                if platform.is_vanished:
                    continue

                for i in range(check_points):
                    test_rect = self.rect.copy()
                    test_rect.y += i * step_y  # 檢查是否與平台發生碰撞
                    if (
                        test_rect.bottom >= platform.rect.top
                        and test_rect.bottom <= platform.rect.bottom
                        and test_rect.right >= platform.rect.left
                        and test_rect.left <= platform.rect.right
                    ):
                        self.rect.bottom = platform.rect.top  # 將玩家放在平台上
                        self.on_platform = True

                        # 如果是特殊平台，標記為已消失
                        if platform.is_special:
                            platform.is_vanished = True
                            # 播放破壞音效
                            if broke_sound:
                                broke_sound.play()

                        # 先設定一般跳躍力
                        self.velocity_y = self.jump_power
                        # 播放跳躍音效
                        if jump_sound:
                            jump_sound.play()

                        # 再檢查是否碰到彈簧（僅檢查當前平台上的彈簧）
                        for spring in springs:
                            if (
                                spring.platform == platform  # 確保彈簧屬於當前平台
                                and test_rect.right
                                >= spring.rect.left  # 檢查水平方向的碰撞
                                and test_rect.left
                                <= spring.rect.right  # 檢查水平方向的碰撞
                            ):
                                self.velocity_y = -25  # 碰到彈簧時給予更強的跳躍力
                                # 播放彈簧音效
                                if spring_sound:
                                    spring_sound.play()
                                break  # 找到彈簧就結束檢查
                        return True
        return False


class Platform:
    def __init__(self, x, y, width, height, color, sprites=None):
        """
        初始化平台\n
        x, y: 平台的左上角座標\n
        width, height: 平台的寬度和高度\n
        color: 平台的顏色 (RGB格式)\n
        sprites: 精靈圖片字典
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.is_special = False  # 是否為特殊平台(只能踩一次)
        self.is_vanished = False  # 特殊平台是否已經消失
        self.sprites = sprites  # 儲存精靈圖片

    def draw(self, display_area):
        """
        繪製平台\n
        display_area: 繪製平台的目標視窗\n
        """
        if not self.is_vanished:  # 只繪製未消失的平台
            if self.sprites:  # 如果有精靈圖片
                sprite_key = "break_platform" if self.is_special else "std_platform"
                if sprite_key in self.sprites:
                    sprite = self.sprites[sprite_key]
                    # 調整精靈大小以符合平台實際尺寸
                    scaled_sprite = pygame.transform.scale(
                        sprite, (self.rect.width, self.rect.height)
                    )
                    display_area.blit(scaled_sprite, self.rect)
                else:
                    pygame.draw.rect(display_area, self.color, self.rect)
            else:
                pygame.draw.rect(display_area, self.color, self.rect)


class Spring:
    def __init__(self, platform, sprites=None):
        """
        初始化彈簧道具\n
        platform: 彈簧所在的平台物件\n
        sprites: 精靈圖片字典\n
        """
        self.width = 20  # 彈簧寬度
        self.height = 10  # 彈簧高度
        # 將彈簧放在平台的隨機位置上
        self.rect = pygame.Rect(
            random.randint(platform.rect.left, platform.rect.right - self.width),
            platform.rect.top - self.height,
            self.width,
            self.height,
        )
        self.color = (255, 255, 0)  # 黃色（當沒有圖片時使用）
        self.platform = platform  # 記錄所屬平台
        self.sprites = sprites  # 儲存精靈圖片

    def draw(self, display_area):
        """
        繪製彈簧\n
        display_area: 繪製彈簧的目標視窗\n
        """
        if self.sprites and "spring_normal" in self.sprites:
            sprite = self.sprites["spring_normal"]
            # 調整精靈大小以符合彈簧實際尺寸
            scaled_sprite = pygame.transform.scale(
                sprite, (self.rect.width, self.rect.height)
            )
            display_area.blit(scaled_sprite, self.rect)
        else:
            pygame.draw.rect(display_area, self.color, self.rect)

    def update_position(self):
        """
        更新彈簧位置\n
        讓彈簧跟著平台移動\n
        """
        # 計算彈簧與平台的相對位置
        platform_top = self.platform.rect.top
        self.rect.bottom = platform_top


class Propeller:
    def __init__(self, platform, sprites=None):
        """
        初始化飛行帽道具\n
        platform: 道具所在的平台物件\n
        sprites: 精靈圖片字典\n
        """
        self.width = 68  # 飛行帽寬度（符合精靈圖片尺寸）
        self.height = 44  # 飛行帽高度（符合精靈圖片尺寸）
        # 將飛行帽放在平台的隨機位置上
        self.rect = pygame.Rect(
            random.randint(platform.rect.left, platform.rect.right - self.width),
            platform.rect.top - self.height,
            self.width,
            self.height,
        )
        self.color = (0, 0, 255)  # 藍色（當沒有精靈圖片時使用）
        self.platform = platform  # 記錄所屬平台，用於同步移動
        self.sprites = sprites  # 儲存精靈圖片
        self.active = False  # 標記是否已被使用

    def draw(self, display_area):
        """
        繪製飛行帽\n
        display_area: 繪製飛行帽的目標視窗\n
        """
        if not self.active:  # 只在未被使用時繪製
            if self.sprites and "propeller" in self.sprites:
                sprite = self.sprites["propeller"]
                # 調整精靈大小以符合實際尺寸
                scaled_sprite = pygame.transform.scale(
                    sprite, (self.width, self.height)
                )
                display_area.blit(scaled_sprite, self.rect)
            else:
                pygame.draw.rect(display_area, self.color, self.rect)

    def update_position(self):
        """
        更新飛行帽位置\n
        讓飛行帽跟隨平台移動\n
        """
        if not self.active:  # 只在未被使用時更新位置
            self.rect.bottom = self.platform.rect.top


######################初始化設定######################
pygame.init()  # 初始化 pygame
pygame.mixer.init()  # 初始化音訊混音器
# 載入跳躍音效
try:
    jump_sound = pygame.mixer.Sound("sound/jump.mp3")  # 載入跳躍音效
    print(f"成功載入跳躍音效")
except Exception as e:
    print(f"無法載入跳躍音效: {e}")
    jump_sound = None  # 設為None以便之後檢查

# 載入彈簧音效
try:
    spring_sound = pygame.mixer.Sound("sound/spring.mp3")  # 載入彈簧音效
    print(f"成功載入彈簧音效")
except Exception as e:
    print(f"無法載入彈簧音效: {e}")
    spring_sound = None  # 設為None以便之後檢查

# 載入飛行帽音效
try:
    propeller_sound = pygame.mixer.Sound("sound/propeller.mp3")  # 載入飛行帽音效
    print(f"成功載入飛行帽音效")
except Exception as e:
    print(f"無法載入飛行帽音效: {e}")
    propeller_sound = None

# 載入破壞音效
try:
    broke_sound = pygame.mixer.Sound("sound/broke.mp3")  # 載入破壞音效
    print(f"成功載入破壞音效")
except Exception as e:
    print(f"無法載入破壞音效: {e}")
    broke_sound = None

FPS = pygame.time.Clock()  # 創建時鐘物件，用於控制遊戲更新速率

######################遊戲視窗設定######################
bg_x = 400  # 設定視窗寬度
bg_y = 600  # 設定視窗高度
bg_size = (bg_x, bg_y)  # 視窗尺寸元組
pygame.display.set_caption("Doodle Jump")  # 設定視窗標題
screen = pygame.display.set_mode(bg_size)  # 創建遊戲視窗

######################主角設定######################
player_w = 50  # 主角寬度（調整為符合精靈圖片）
player_h = 50  # 主角高度（調整為符合精靈圖片）
player_x = (bg_x - player_w) // 2  # 計算主角的初始X座標（置中）
player_y = bg_y - player_h - 50  # 計算主角的初始Y座標（底部上方50像素）

# 載入圖片並實例化玩家
try:
    # 載入遊戲所需的所有精靈圖片（需要在設置視窗模式後進行）
    sprites = load_doodle_sprites()
    use_sprites = True  # 標記是否使用精靈圖片
    print(f"成功載入 {len(sprites)} 個精靈圖片")
except Exception as e:
    # 如果載入失敗，使用簡單的幾何圖形代替
    print(f"載入精靈圖片時發生錯誤: {e}")
    print("將使用簡單圖形進行遊戲")
    sprites = None
    use_sprites = False  # 標記不使用精靈圖片

# 創建主角物件，傳入精靈參數
player = Player(
    player_x,
    player_y,
    player_w,
    player_h,
    (0, 255, 0),
    sprites if use_sprites else None,
)

######################平台設定######################
platform_w = 70  # 平台寬度（調整為符合精靈圖片）
platform_h = 20  # 平台高度（調整為符合精靈圖片）
platforms = []  # 建立平台列表
springs = []  # 建立彈簧列表
propellers = []  # 建立飛行帽列表

# 創建底部平台，確保玩家不會掉出畫面
platform_x = (bg_x - platform_w) // 2  # 平台X座標（置中）
platform_y = bg_y - platform_h - 10  # 平台Y座標（底部上方10像素）
# 創建平台物件，設定為白色並傳入精靈
platform = Platform(
    platform_x,
    platform_y,
    platform_w,
    platform_h,
    (255, 255, 255),
    sprites if use_sprites else None,
)
platforms.append(platform)

# 隨機生成其他平台
platform_count = random.randint(8, 10) + 10  # 隨機決定平台數量
for i in range(platform_count):
    x = random.randint(0, bg_x - platform_w)  # 隨機生成平台的X座標
    y = (bg_y - 100) - (i * 60)  # 確保平台間距60像素
    platform = Platform(
        x, y, platform_w, platform_h, (255, 255, 255), sprites if use_sprites else None
    )
    platforms.append(platform)
    # 有20%機率在平台上生成彈簧
    if random.random() < 0.2:
        spring = Spring(platform, sprites if use_sprites else None)
        springs.append(spring)


######################字型設定######################
font = pygame.font.Font(
    "C:/Windows/Fonts/msjh.ttc", 24
)  # 設定字型和大小為微軟正黑體24點


######################主程式######################
# 更新相機位置的函式
def update_camera():
    """
    更新相機位置和平台\n
    - 當玩家上升到螢幕的一半高度以上時，固定玩家在螢幕中間\n
    - 將所有平台往下移動，製造出玩家繼續往上的錯覺\n
    - 移除超出畫面底部的平台\n
    - 在上方生成新的平台\n
    """
    global score, initial_player_y  # 使用全域變數
    screen_middle = bg_y // 2  # 螢幕中間的Y座標
    # 如果玩家位置高於螢幕中間，更新相機位置
    if player.rect.y < screen_middle:
        camera_move = screen_middle - player.rect.y
        player.rect.y = screen_middle

        # 計算分數：每上升10像素加1分
        score += int(camera_move / 10)

        # 更新所有平台的位置
        for platform in platforms:
            platform.rect.y += camera_move  # 更新所有彈簧和飛行帽的位置
        for spring in springs[:]:  # 使用切片來建立列表複本
            spring.rect.y += camera_move
            # 移除超出畫面或已啟用的彈簧
            if spring.rect.top > bg_y or spring.platform not in platforms:
                springs.remove(spring)

        for propeller in propellers[:]:  # 使用切片來建立列表複本
            propeller.rect.y += camera_move
            # 移除超出畫面或已啟用的飛行帽
            if propeller.rect.top > bg_y or propeller.platform not in platforms:
                propellers.remove(propeller)

        # 移除超出畫面底部的平台
        y_min = bg_y
        for platform in platforms[:]:  # 使用切片來建立列表複本
            if platform.rect.top > bg_y:
                platforms.remove(platform)
            if platform.rect.top < y_min:
                y_min = platform.rect.top

        # 在上方生成新的平台
        if len(platforms) < platform_count:
            x = random.randint(0, bg_x - platform_w)
            y = y_min - 60  # 確保新平台在最上方
            platform = Platform(
                x,
                y,
                platform_w,
                platform_h,
                (255, 255, 255),
                sprites if use_sprites else None,
            )  # 當分數超過100分時，有20%機率生成特殊平台
            if score > 100 and random.random() < 0.2:
                platform.is_special = True  # 設定為特殊平台
                platform.color = (255, 0, 0)  # 設定為紅色

            platforms.append(platform)

            # 在非特殊平台上生成道具
            if not platform.is_special:
                # 有20%機率生成彈簧
                if random.random() < 0.2:
                    spring = Spring(platform, sprites if use_sprites else None)
                    springs.append(spring)
                # 在200分以上時才有5%機率生成飛行帽
                elif random.random() < 0.05 and score > 200:
                    propeller = Propeller(platform, sprites if use_sprites else None)
                    propellers.append(propeller)


def reset_game():
    """
    重置遊戲狀態\n
    - 重設玩家位置\n
    - 清空並重新生成平台\n
    - 重設分數和遊戲狀態\n
    """
    global score, game_over, platforms, springs, initial_player_y, highest_score, propellers

    score = 0  # 重設分數
    # 重設玩家位置
    player.rect.x = (bg_x - player_w) // 2
    player.rect.y = bg_y - player_h - 50
    player.velocity_y = 0  # 清空所有道具列表
    platforms.clear()
    springs.clear()
    propellers.clear()
    player.flying = False  # 重置飛行狀態

    # 重新生成底部平台
    platform_x = (bg_x - platform_w) // 2
    platform_y = bg_y - platform_h - 10
    platform = Platform(
        platform_x,
        platform_y,
        platform_w,
        platform_h,
        (255, 255, 255),
        sprites if use_sprites else None,
    )
    platforms.append(platform)

    # 重新生成其他平台
    for i in range(platform_count - 1):
        x = random.randint(0, bg_x - platform_w)
        y = (bg_y - 100) - (i * 60)
        platform = Platform(
            x,
            y,
            platform_w,
            platform_h,
            (255, 255, 255),
            sprites if use_sprites else None,
        )
        platforms.append(platform)
        # 在非特殊平台上生成道具
        if not platform.is_special:
            # 有20%機率生成彈簧
            if random.random() < 0.2:
                spring = Spring(platform, sprites if use_sprites else None)
                springs.append(spring)
            # 在200分以上時才有5%機率生成飛行帽
            elif random.random() < 0.05 and score > 200:
                propeller = Propeller(platform, sprites if use_sprites else None)
                propellers.append(propeller)

    # 重設遊戲相關變數
    game_over = False
    initial_player_y = player.rect.y


while True:
    FPS.tick(60)  # 限制遊戲更新率為每秒60幀
    screen.fill((255, 255, 255))  # 用白色填充畫面背景

    if not game_over:  # 遊戲進行中
        update_camera()  # 更新相機位置和平台

        # 獲取當前按下的按鍵狀態
        keys = pygame.key.get_pressed()

        # 處理左右移動控制
        if keys[pygame.K_LEFT]:  # 當按下左方向鍵
            player.move(-1, bg_x)  # 向左移動
        if keys[pygame.K_RIGHT]:  # 當按下右方向鍵
            player.move(1, bg_x)  # 向右移動        # 應用重力效果和處理碰撞
        player.apply_gravity()
        player.check_platform_collision(platforms, propellers)

        # 更新道具位置
        for spring in springs:
            spring.update_position()
        for propeller in propellers:
            propeller.update_position()

        # 檢查遊戲結束條件（玩家掉出畫面）
        if player.rect.top > bg_y:
            game_over = True
            # 更新最高分數
            if score > highest_score:
                highest_score = score

    # 事件處理迴圈
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 當使用者點擊關閉視窗
            sys.exit()  # 結束程式
        elif event.type == pygame.KEYDOWN and game_over:  # 遊戲結束時按任意鍵重新開始
            reset_game()  # 繪製所有平台和道具
    for platform in platforms:
        platform.draw(screen)  # 繪製平台
    for spring in springs:
        spring.draw(screen)  # 繪製彈簧
    for propeller in propellers:
        propeller.draw(screen)  # 繪製飛行帽
    for propeller in propellers:
        propeller.draw(screen)  # 繪製飛行帽

    player.draw(screen)  # 繪製主角

    # 顯示分數
    score_text = font.render(f"分數: {score}", True, (0, 0, 0))  # 使用黑色文字
    screen.blit(score_text, (10, 10))

    # 如果遊戲結束，顯示遊戲結束訊息和最高分
    if game_over:
        game_over_text = font.render(
            "遊戲結束！按任意鍵重新開始", True, (0, 0, 0)
        )  # 使用黑色文字
        highest_score_text = font.render(
            f"最高分數: {highest_score}", True, (0, 0, 0)
        )  # 使用黑色文字
        text_rect = game_over_text.get_rect(center=(bg_x / 2, bg_y / 2))
        score_rect = highest_score_text.get_rect(center=(bg_x / 2, bg_y / 2 + 40))
        screen.blit(game_over_text, text_rect)
        screen.blit(highest_score_text, score_rect)

    pygame.display.update()  # 更新畫面顯示
