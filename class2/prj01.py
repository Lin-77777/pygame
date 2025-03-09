######################載入套件######################
import pygame
import sys


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
brickA = Brick(100, 100, 50, 20, (255, 0, 0))  # 磚塊A
brickB = Brick(200, 100, 50, 20, (0, 255, 0))  # 磚塊B
######################顯示文字設定######################

######################底板設定######################

######################球設定######################

######################遊戲結束設定######################

######################主程式######################
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 點擊關閉視窗
            sys.exit()
    brickA.rect.x = 100  # 磚塊A向右移動
    brickA.rect.y = 200  # 磚塊B向右移動
    brickA.rect.width = 70  # 磚塊A寬度
    brickA.rect.height = 50  # 磚塊A高度
    brickA.draw(screen)  # 畫出磚塊A
    brickB.draw(screen)  # 畫出磚塊B

    pygame.display.update()  # 更新畫面
