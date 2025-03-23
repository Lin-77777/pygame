######################載入套件######################
import pygame
import sys
import random as r


######################物件類別######################
class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 30
        self.is_active = True

    def update(self):
        if self.radius < self.max_radius:
            self.radius += 2
        else:
            self.is_active = False

    def draw(self, display_area):
        if self.is_active:
            pygame.draw.circle(
                display_area, (255, 165, 0), (int(self.x), int(self.y)), self.radius
            )


class Brick:
    def __init__(self, x, y, width, height, color, can_explode=True):
        """
        初始化磚塊\n
        x,y:磚塊的左上角座標\n
        width,height:磚塊的寬度與高度\n
        color:磚塊顏色\n
        can_explode:是否可以成為炸彈塊\n
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hit = False
        self.is_explosive = (
            can_explode and r.random() < 0.1
        )  # 只有在可以爆炸的情況下才有機會成為炸彈塊
        if self.is_explosive:
            self.color = (255, 69, 0)  # 爆炸方塊為橘紅色

    def draw(self, display_area):
        """
        畫出磚塊\n
        display_area:繪製磚塊的區域\n
        """
        if not self.hit:
            pygame.draw.rect(display_area, self.color, self.rect)
            if self.is_explosive:
                # 畫一個"X"標記表示這是爆炸方塊
                pygame.draw.line(
                    display_area,
                    (255, 255, 255),
                    (self.rect.x, self.rect.y),
                    (self.rect.x + self.rect.width, self.rect.y + self.rect.height),
                )
                pygame.draw.line(
                    display_area,
                    (255, 255, 255),
                    (self.rect.x + self.rect.width, self.rect.y),
                    (self.rect.x, self.rect.y + self.rect.height),
                )


class Ball:
    def __init__(self, x, y, radius, color):
        """
        初始化球\n
        x,y:球的圓心座標\n
        radius:球的半徑\n
        color:球的顏色\n
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed_x = 3  # 降低初始水平速度
        self.speed_y = -3  # 降低初始垂直速度(負數表示向上)
        self.is_moving = False  # 是否正在移動
        self.score = 0  # 新增分數屬性

    def move(self):
        """
        移動球\n
        """
        if self.is_moving:
            self.x += self.speed_x
            self.y += self.speed_y

    def draw(self, display_area):
        """
        畫出球\n
        display_area:繪製球的區域\n
        """
        pygame.draw.circle(
            display_area, self.color, (int(self.x), int(self.y)), self.radius
        )

    def check_collision(self, bg_x, bg_y, bricks, pad, lives):
        """
        檢查球與磚塊的碰撞\n
        bg_x,bg_y:視窗的寬度與高度\n
        bricks:磚塊列表\n
        pad:底板物件\n
        lives:生命值\n
        """
        # 檢查球是否碰到邊界
        if self.x - self.radius <= 0 or self.x + self.radius >= bg_x:
            self.speed_x = -self.speed_x  # 水平反彈
        if self.y - self.radius <= 0:
            self.speed_y = -self.speed_y  # 垂直反彈

        # 檢查球是否碰到底部(失去生命值)
        if self.y + self.radius >= bg_y:
            self.is_moving = False  # 停止移動
            return lives - 1, []  # 當球碰到底部時，回傳生命值減1和空的爆炸列表
        # 改進與底板的碰撞檢查
        if (
            self.y + self.radius >= pad.rect.y
            and self.y + self.radius <= pad.rect.y + pad.rect.height
            and self.x >= pad.rect.x
            and self.x <= pad.rect.x + pad.rect.width
        ):
            self.speed_y = -abs(self.speed_y)

        # 檢查球是否碰到磚塊
        explosions = []
        for brick in bricks:
            if not brick.hit:  # 只檢查未被擊中的磚塊
                # 計算球心到磚塊的距離
                dx = abs(self.x - (brick.rect.x + brick.rect.width // 2))
                dy = abs(self.y - (brick.rect.y + brick.rect.height // 2))
                # 檢查是否碰撞
                if dx <= (self.radius + brick.rect.width / 2) and dy <= (
                    self.radius + brick.rect.height / 2
                ):
                    brick.hit = True  # 標記磚塊為已擊中
                    self.score += 100  # 擊中磚塊加100分
                    if brick.is_explosive:
                        explosions.append(
                            Explosion(brick.rect.centerx, brick.rect.centery)
                        )
                        # 爆炸會影響周圍的方塊
                        for other_brick in bricks:
                            if not other_brick.hit:
                                distance = (
                                    (other_brick.rect.centerx - brick.rect.centerx) ** 2
                                    + (other_brick.rect.centery - brick.rect.centery)
                                    ** 2
                                ) ** 0.5
                                if distance < 100:  # 爆炸範圍
                                    other_brick.hit = True
                                    self.score += 50
                    # 從磚塊哪邊碰撞再決定反彈反方向
                    if (
                        self.x < brick.rect.x
                        or self.x > brick.rect.x + brick.rect.width
                    ):
                        self.speed_x = -self.speed_x  # 水平反彈
                    else:
                        self.speed_y = -self.speed_y  # 垂直反彈

        return lives, explosions  # 如果沒碰到底部，回傳原本的生命值


######################定義函式區######################

######################初始化設定######################
pygame.init()  # 初始化pygame
FPS = pygame.time.Clock()  # 設定FPS
pygame.font.init()  # 初始化字型
font = pygame.font.Font(None, 36)  # 建立字型物件
lives = 10  # 初始生命值為10
######################載入圖片######################

######################遊戲視窗設定######################
bg_x = 800  # 視窗寬度
bg_y = 600  # 視窗高度
bg_size = (bg_x, bg_y)  # 視窗大小
pygame.display.set_caption("打磚塊遊戲")  # 設定視窗標題
screen = pygame.display.set_mode(bg_size)  # 設定視窗大小

######################磚塊######################
bricks_row = 9  # row=9 為衡的有九個磚塊
bricks_col = 11  # col=11 為直的有五個磚塊
bricks_w = 58  # 磚塊寬度
bricks_h = 20  # 磚塊高度
bricks_gap = 5  # 磚塊間距
bricks = []  # 用來存放磚塊物件的列表
for row in range(bricks_row):
    for col in range(bricks_col):
        x = col * (bricks_w + bricks_gap) + 55  # 55是磚塊的起始X座標
        y = row * (bricks_h + bricks_gap) + 60  # 磚塊的起始Y座標
        color = (
            r.randint(30, 255),
            r.randint(30, 255),
            r.randint(30, 255),
        )  # 磚塊顏色RGB隨機產生
        brick = Brick(x, y, bricks_w, bricks_h, color)  # 建立磚塊物件
        bricks.append(brick)  # 將磚塊物件加入列表

######################顯示文字設定######################

######################底板設定######################
pad = Brick(
    0, bg_y - 50, bricks_w, bricks_h, (255, 255, 255), can_explode=False
)  # 設定底板不可成為炸彈塊
######################球設定######################
ball_radius = 10  # 球的半徑
ball_color = (255, 215, 0)  # 球的顏為金色
ball = Ball(
    pad.rect.x + pad.rect.width // 2, pad.rect.y - ball_radius, ball_radius, ball_color
)  # 球的設定
######################遊戲結束設定######################

######################主程式######################
explosions = []  # 存放爆炸特效

while True:
    FPS.tick(120)  # 設定FPS為60
    screen.fill((0, 0, 0))  # 清空畫面
    mos_x, mos_y = pygame.mouse.get_pos()  # 取得滑鼠座標
    pad.rect.x = mos_x - pad.rect.width // 2  # 以滑鼠的中心為底板的中心

    if pad.rect.x < 0:  # 如果底板的X座標小於0
        pad.rect.x = 0

    if (
        pad.rect.x + pad.rect.width > bg_x
    ):  # 如果底板的X座標加上底板的寬度大於視窗的寬度
        pad.rect.x = bg_x - pad.rect.width
    if not ball.is_moving:  # 如果球沒有移動
        ball.x = (
            pad.rect.x + pad.rect.width // 2
        )  # 球的X座標為底板的X座標加上底板的寬度的一半
        ball.y = pad.rect.y - ball_radius  # 球的Y座標為底板的Y座標減去球的半徑
    else:
        ball.move()  # 移動球
        lives, new_explosions = ball.check_collision(
            bg_x, bg_y, bricks, pad, lives
        )  # 更新生命值
        explosions.extend(new_explosions)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 點擊關閉視窗
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:  # 點擊滑鼠
            # 點擊滑鼠開始移動球
            if not ball.is_moving:
                ball.is_moving = True
    for brick in bricks:
        brick.draw(screen)  # 繪製磚塊
    pad.draw(screen)  # 繪製底板
    ball.draw(screen)  # 繪製球

    # 繪製分數和生命值
    score_text = font.render(f"Score: {ball.score}", True, (255, 255, 255))
    lives_text = font.render(f"Lives: {lives}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (bg_x - 120, 10))

    # 檢查遊戲結束條件
    if lives <= 0:
        game_over_text = font.render("Game Over!", True, (255, 0, 0))
        screen.blit(game_over_text, (bg_x // 2 - 100, bg_y // 2))
        pygame.display.update()
        pygame.time.wait(2000)  # 等待2秒
        sys.exit()

    # 更新和繪製爆炸特效
    for explosion in explosions[:]:
        explosion.update()
        explosion.draw(screen)
        if not explosion.is_active:
            explosions.remove(explosion)

    pygame.display.update()  # 更新畫面
