######################載入套件######################
import pygame
import sys
import random as r


######################物件類別######################
class Brick:
    def __init__(self, x, y, width, height, color):
        """
        初始化磚塊\n
        x,y:磚塊的左上角座標\n
        width,height:磚塊的寬度與高度\n
        color:磚塊顏色\n
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hit = False

    def draw(self, display_area):
        """
        畫出磚塊\n
        display_area:繪製磚塊的區域\n
        """
        if not self.hit:
            pygame.draw.rect(display_area, self.color, self.rect)


######################定義函式區######################

######################初始化設定######################
pygame.init()  # 初始化pygame
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

######################球設定######################

######################遊戲結束設定######################

######################主程式######################

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 點擊關閉視窗
            sys.exit()
    screen.fill((0, 0, 0))  # 清空畫面
    for brick in bricks:
        brick.draw(screen)  # 繪製磚塊
    x1, y1 = pygame.mouse.get_pos()
    pygame.draw.rect(screen, (255, 255, 255), (x1, 530, 80, 15))

    pygame.display.update()  # 更新畫面
