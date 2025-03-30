######################載入套件######################
import pygame
import sys


######################物件類別######################
class Player:
    def __init__(self, x, y, width, height):
        """
        初始化主角\n
        x,y: 主角的左上角座標\n
        width,height: 主角的寬度與高度\n
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (0, 255, 0)  # 主角顏色為綠色

    def draw(self, display_area):
        """
        畫出主角\n
        display_area: 繪製主角的區域\n
        """
        pygame.draw.rect(display_area, self.color, self.rect)


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

######################主程式######################
while True:
    FPS.tick(60)  # 設定FPS為60
    screen.fill((0, 0, 0))  # 設定背景為黑色

    # 事件處理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 點擊關閉視窗
            pygame.quit()
            sys.exit()

    # 繪製主角
    player.draw(screen)

    # 更新畫面
    pygame.display.update()
