import heapq
from collections import defaultdict

import numpy as np
from tqdm import tqdm


class State:
    def __init__(self, game: 'Klotski', board):
        self.game = game
        self.board = board
        self.pattern = np.copy(board)
        for idx in self.game.block_indices:
            num_blocks = self.game.block_indices[idx]
            self.pattern[np.where(self.board == idx)] = num_blocks

    def __hash__(self):
        return hash(tuple(self.pattern.flatten().tolist()))

    def __eq__(self, other):
        return np.array_equal(self.pattern, other.pattern)
    
    def __repr__(self):
        return str(self.board)
    
    def __gt__(self, other):
        return True
    
    def move_(self, block_idx, dx, dy, xs=None, ys=None):
        if xs is None or ys is None:
            xs, ys = np.where(self.board == block_idx)
        new_xs = xs + dx
        new_ys = ys + dy
        if np.all((new_xs >= 0) & (new_xs < self.board.shape[0]) &
                  (new_ys >= 0) & (new_ys < self.board.shape[1])):
            # 创建一个条件数组，检查是否每个新位置要么是空要么是当前的block_idx
            condition = (self.board[new_xs, new_ys] == self.game.empty) | (self.board[new_xs, new_ys] == block_idx)
            if np.all(condition):
                new_board = np.copy(self.board)
                new_board[xs, ys] = self.game.empty
                new_board[new_xs, new_ys] = block_idx
                return State(self.game, new_board)
        return None  # 不可移动
        
    def next_states(self):
        for block_idx in self.game.block_indices:
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            xs, ys = np.where(self.board == block_idx)
            for dx, dy in directions:
                new_state = self.move_(block_idx, dx, dy, xs, ys)
                if new_state is not None:
                    yield (block_idx, dx, dy), new_state

    def is_terminal(self) -> bool:
        return np.all(self.board[self.game.end_region] == self.game.end_pattern[self.game.end_region])


class Klotski:

    def __init__(self, board, end_pattern, empty=0):
        self.block_indices = {idx: np.sum(board == idx) for idx in np.unique(board) if idx != empty}
        self.state = State(self, board)
        self.empty = empty
        self.end_pattern = end_pattern
        self.end_region = end_pattern != empty
        self.end_indices = np.unique(self.end_region)
        
    def move(self, block_idx, dx, dy) -> None:
        new_state = self.state.move_(block_idx, dx, dy)
        if new_state is not None:
            self.state = new_state
        
    def h(self, state):
        # 计算 h(n)，即从当前状态到目标状态的预估成本
        total_dist = 0
        for idx in self.end_indices:
            state_pos = np.where(state.board == idx)
            end_pos = np.where(self.end_pattern == idx)
            if len(state_pos[0]) > 0:
                dist = abs(state_pos[0][0] - end_pos[0][0]) + abs(state_pos[1][0] - end_pos[1][0])
                total_dist += dist
        return total_dist
    
    def a_star(self):
        open_set = []  # 优先队列
        heapq.heappush(open_set, (0 + self.h(self.state), self.state, []))  # (f(n), 状态, 路径)
        visited = {self.state}
        g_scores = defaultdict(lambda: float('inf'))  # 从起始点到当前点的成本
        g_scores[self.state] = 0
        
        p_bar = tqdm()
        while open_set:
            _, current_state, path = heapq.heappop(open_set)
            
            if current_state.is_terminal():
                return path
            
            for action, next_state in current_state.next_states():
                p_bar.update()
                tentative_g_score = g_scores[current_state] + 1  # 假设每步成本为1
                if tentative_g_score < g_scores[next_state]:
                    g_scores[next_state] = tentative_g_score
                    h_score = self.h(next_state) * 100
                    f_score = tentative_g_score + h_score
                    if next_state not in visited:
                        visited.add(next_state)
                        heapq.heappush(open_set, (f_score, next_state, path + [(action, next_state)]))
        p_bar.close()
        return None


if __name__ == "__main__":
    # 使用示例
    board = np.array([[10, 1, 1, 2],
                      [10, 1, 1, 2],
                      [3, 4, 4, 5],
                      [3, 6, 7, 5],
                      [8, 0, 0, 9]])
    
    end_pattern = np.array([[0, 0, 0, 0],
                            [0, 0, 0, 0],
                            [0, 0, 0, 0],
                            [0, 1, 1, 0],
                            [0, 1, 1, 0]])
    klotski = Klotski(board, end_pattern)
    
    solution_path = klotski.a_star()
    
    # 如果你想查看解决方案路径中的每个步骤，可以按以下方式打印：
    for (block_idx, dx, dy), state in solution_path:
        print((block_idx, dx, dy))
        print(state)
