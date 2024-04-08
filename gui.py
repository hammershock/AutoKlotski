import time

import pygame
import numpy as np
from klotski_ import Klotski


class KlotskiGUI:
    def __init__(self, board, end_pattern, empty=0, block_width_pixels=100):
        # 初始化 Pygame
        pygame.init()
        
        # 定义颜色
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.COLORS = [(140, 115, 111), (170, 184, 171), (197, 171, 137),
                       (151, 102, 102), (140, 115, 111), (221, 208, 200),
                       (160, 136, 135), (226, 198, 196), (177, 172, 179), (83, 86, 92)]
        
        # 设置屏幕大小和标题
        self.block_size_pixels = block_width_pixels  # 单个方块所占像素
        self.height, self.width = board.shape
        self.screen_width, self.screen_height = self.width * self.block_size_pixels, self.height * self.block_size_pixels
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Klotski')
        
        # 实例化 Klotski 游戏
        self.game = Klotski(board, end_pattern, empty=empty)
        
        self.running = True
        self.dragging = False
        self.drag_start_pos = None
    
    def draw_board(self, board):
        """绘制棋盘和方块，相同色块之间的边线使用对应颜色填充"""
        for i in range(self.height):
            for j in range(self.width):
                block_value = board[i][j]
                if block_value != 0:
                    color_idx = np.sum(board == block_value)
                    block_color = self.COLORS[color_idx % len(self.COLORS)]
                    rect = pygame.Rect(j * self.block_size_pixels, i * self.block_size_pixels, self.block_size_pixels, self.block_size_pixels)
                    pygame.draw.rect(self.screen, block_color, rect)
                    
                    # 检查右侧方块是否相同
                    if j < self.width - 1 and board[i][j] == board[i][j + 1]:
                        right_border = pygame.Rect((j + 1) * self.block_size_pixels - 3, i * self.block_size_pixels, 3, self.block_size_pixels)
                        pygame.draw.rect(self.screen, block_color, right_border)
                    
                    # 检查下方方块是否相同
                    if i < self.height - 1 and board[i][j] == board[i + 1][j]:
                        bottom_border = pygame.Rect(j * self.block_size_pixels, (i + 1) * self.block_size_pixels - 3, self.block_size_pixels, 3)
                        pygame.draw.rect(self.screen, block_color, bottom_border)
                    
                    # 绘制剩余的方块边框
                    if j == self.width - 1 or board[i][j] != board[i][j + 1]:
                        pygame.draw.line(self.screen, self.BLACK, (rect.right - 1, rect.top), (rect.right - 1, rect.bottom), 3)
                    if i == self.height - 1 or board[i][j] != board[i + 1][j]:
                        pygame.draw.line(self.screen, self.BLACK, (rect.left, rect.bottom - 1), (rect.right, rect.bottom - 1), 3)
                    if j == 0 or board[i][j] != board[i][j - 1]:
                        pygame.draw.line(self.screen, self.BLACK, (rect.left, rect.top), (rect.left, rect.bottom), 3)
                    if i == 0 or board[i][j] != board[i - 1][j]:
                        pygame.draw.line(self.screen, self.BLACK, (rect.left, rect.top), (rect.right, rect.top), 3)
                    
    def get_block_idx(self, drag_start_pos):
        """
        根据鼠标点击位置，找到对应的方块标号。
        :param drag_start_pos: 鼠标点击的位置，格式为 (x, y)。
        :return: 如果点击位置有效，则返回方块的标号；否则返回 None。
        """
        x, y = drag_start_pos
        j = x // self.block_size_pixels  # 计算列索引
        i = y // self.block_size_pixels  # 计算行索引
        
        if i < self.height and j < self.width:  # 确保索引在棋盘范围内
            return self.game.state.board[i, j]
        return None
    
    def run(self):
        """运行游戏的主循环"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # 开始拖动
                    self.dragging = True
                    self.drag_start_pos = event.pos
                elif event.type == pygame.MOUSEBUTTONUP and self.dragging:
                    # 结束拖动
                    self.dragging = False
                    drag_end_pos = event.pos
                    
                    # 计算拖动方向和距离
                    dx = drag_end_pos[0] - self.drag_start_pos[0]
                    dy = drag_end_pos[1] - self.drag_start_pos[1]
                    
                    # 确定拖动方向
                    direction_x = 0
                    direction_y = 0
                    if abs(dx) > abs(dy):  # 水平方向
                        if abs(dx) > 40:  # 拖动距离超过40像素
                            direction_y = int(np.sign(dx))
                    else:  # 垂直方向
                        if abs(dy) > 40:
                            direction_x = int(np.sign(dy))
                    
                    if direction_x != 0 or direction_y != 0:
                        block_idx = self.get_block_idx(self.drag_start_pos)
                        if block_idx is not None:
                            self.game.move(block_idx, direction_x, direction_y)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:  # 如果按下 's' 键
                        start_time = time.time()
                        solution_path = self.game.a_star(accelerate=True)  # 获取解法路径
                        end_time = time.time()
                        print("Time elapsed: " + str(end_time - start_time))
                        if solution_path is not None:
                            for action, _ in solution_path:
                                block_idx, dx, dy = action
                                self.game.move(block_idx, dx, dy)  # 执行移动
                                # 重新绘制棋盘以显示当前状态
                                self.screen.fill(self.BLACK)
                                self.draw_board(self.game.state.board)
                                pygame.display.flip()
                                pygame.time.wait(50)  # 等待200毫秒以方便观察
                        else:
                            print("No solution found")
            
            self.screen.fill(self.BLACK)
            self.draw_board(self.game.state.board)
            pygame.display.flip()
        
        pygame.quit()


if __name__ == "__main__":
    board = np.array([[10, 1, 1, 2],
                      [3, 1, 1, 4],
                      [3, 5, 5, 4],
                      [6, 7, 7, 8],
                      [0, 9, 9, 0]])
    
    end_pattern = np.array([[0, 0, 0, 0],
                            [0, 0, 0, 0],
                            [0, 0, 0, 0],
                            [0, 1, 1, 0],
                            [0, 1, 1, 0]])
    klotski_gui = KlotskiGUI(board, end_pattern, empty=0, block_width_pixels=100)
    klotski_gui.run()
    
