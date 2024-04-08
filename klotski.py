import heapq
from collections import defaultdict
import sys
import os
import subprocess
import glob


import numpy as np
from tqdm import tqdm


class State:
    def __init__(self, game: 'Klotski', board, parent=None, from_action=None):
        self.game = game
        self.board = board
        self.pattern = self.game.pattern_mapping(board)  # 计算pattern
        self.parent = parent
        self.from_action = from_action

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
        if np.all((new_xs >= 0) & (new_xs < self.board.shape[0]) &  # 确保移动不会出界
                  (new_ys >= 0) & (new_ys < self.board.shape[1])):
            # 确保移动可以进行
            condition = (self.board[new_xs, new_ys] == self.game.empty) | (self.board[new_xs, new_ys] == block_idx)
            if np.all(condition):
                new_board = np.copy(self.board)
                new_board[xs, ys] = self.game.empty
                new_board[new_xs, new_ys] = block_idx
                return State(self.game, new_board, self, (block_idx, dx, dy))
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
        self.board = board
        self.end_pattern = end_pattern
        
        self.block_pattern = defaultdict(list)
        index_map = {}
        for idx in np.unique(board):
            if idx != empty:
                xs, ys = np.where(board == idx)
                xs -= np.min(xs)
                ys -= np.min(ys)
                key = tuple(np.array([xs, ys]).flatten().tolist())
                self.block_pattern[key].append(idx)
        
        n = 0
        for lst in self.block_pattern.values():
            if n == empty:
                n += 1
            for block_idx in lst:
                index_map[block_idx] = n
            n += 1
            
        self.pattern_mapping = np.vectorize(lambda x: index_map.get(x, x))
        
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
    
    def a_star(self, accelerate=False):
        if accelerate:
            try:
                if not len(glob.glob(f'./cpp/build/*.so')):
                    os.system(f'/usr/bin/zsh ./cpp/build.sh')
                return self.a_star_c()
            except ImportError:
                pass
            
        open_set = []  # 优先队列
        heapq.heappush(open_set, (0 + self.h(self.state), self.state))  # (f(n), 状态)
        visited = {self.state}
        g_scores = defaultdict(lambda: float('inf'))  # 从起始点到当前点的成本
        g_scores[self.state] = 0
        
        p_bar = tqdm()
        while open_set:
            _, current_state = heapq.heappop(open_set)
            
            if current_state.is_terminal():
                path = []
                while current_state.parent is not None:
                    path.append((current_state.from_action, current_state))
                    current_state = current_state.parent
                print(f'size: {len(visited)}')
                return path[::-1]
            
            for action, next_state in current_state.next_states():
                p_bar.update()
                tentative_g_score = g_scores[current_state] + 1  # 假设每步成本为1
                if tentative_g_score < g_scores[next_state]:
                    g_scores[next_state] = tentative_g_score
                    h_score = self.h(next_state) * 100
                    f_score = tentative_g_score + h_score
                    if next_state not in visited:
                        visited.add(next_state)
                        heapq.heappush(open_set, (f_score, next_state))
        p_bar.close()
        return None
    
    def a_star_c(self):
        sys.path.append('./cpp/build')
        import klotski_module
        klotski = klotski_module.Klotski(self.state.board.tolist(), self.end_pattern.tolist(), self.empty)
        print('using accelerate mode!')
        solution = klotski.a_star()
        if solution is None:
            return None
        ret = []
        for s in solution:
            ret.append(((s.block_idx, s.dx, s.dy), None))
            # yield (s.block_idx, s.dx, s.dy), None
        print(f'steps: {klotski.steps}')
        return ret
    
    
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
