//
// Created by hammer on 24-4-7.
//

#include "include/State.h"
#include "include/Klotski.h" // 如果State需要访问Klotski中的成员
#include <vector>
#include <unordered_map>
#include <memory>
#include <cmath>
#include <functional>
#include <utility> // 对于std::pair

using namespace std;

State::State(Klotski* game, const vector<vector<int>>& board,
             const unordered_map<int, vector<int>>& xs,
             const unordered_map<int, vector<int>>& ys,
             State* parent, Move from_move, int depth)
        : game(game), board(board), pattern(board), hash_id(0),
          xs(xs), ys(ys), parent(parent), from_move_(from_move), depth(depth) {
    // 如果xs和ys为空，则初始化它们
    if (this->xs.empty() || this->ys.empty()) {
        for (int i = 0; i < board.size(); ++i) {
            for (int j = 0; j < board[i].size(); ++j) {
                int block_idx = board[i][j];
                this->xs[block_idx].push_back(i);
                this->ys[block_idx].push_back(j);
            }
        }
    }

    for (int i = 0; i < pattern.size(); ++i) {
        for (int j = 0; j < pattern[i].size(); ++j) {
            pattern[i][j] = game->blockidx2blocknum_[pattern[i][j]]; // 计算该state的pattern
            hash_combine(hash_id, pattern[i][j]);  // 计算hash值
        }
    }
}

unique_ptr<State> State::move_(Move& move) {
    vector<int> newXs, newYs;
    unordered_map<int, vector<int>> new_xs = this->xs, new_ys = this->ys;
    vector<int> xs = this->xs[move.block_idx], ys = this->ys[move.block_idx];
    
    for (size_t i = 0; i < xs.size(); ++i) {
        int x = xs[i] + move.dx, y = ys[i] + move.dy;
        newXs.push_back(x);
        newYs.push_back(y);
        if (x < 0 || x >= board.size() || y < 0 || y >= board[0].size() ||  // 超出边界，无法移动
            (board[x][y] != game->empty && board[x][y] != move.block_idx))return nullptr;
    }

    vector<vector<int>> newBoard = board;
    for (size_t i = 0; i < xs.size(); ++i) {
        newBoard[xs[i]][ys[i]] = game->empty; // 将原位置设置为empty
    }
    for (size_t i = 0; i < newXs.size(); ++i) {
        newBoard[newXs[i]][newYs[i]] = move.block_idx; // 将新位置设置为block_idx
    }

    new_xs[move.block_idx] = newXs;
    new_ys[move.block_idx] = newYs;

    return unique_ptr<State>(new State(game, newBoard, new_xs, new_ys, this, move, this->depth + 1));
}


vector<pair<Move, unique_ptr<State>>> State::next_states() {
    vector<pair<Move, unique_ptr<State>>> result;
    for (const auto& [block_idx, x_coords] : xs) {
        const auto& y_coords = ys[block_idx];
        if (block_idx == game->empty) continue;
        vector<std::pair<int, int>> directions{{0, -1}, {0, 1}, {-1, 0}, {1, 0}};
        for (const auto& [dx, dy] : directions) {
//            if (dx == -from_move_.dx && dy == -from_move_.dy)continue;
            Move move{block_idx, dx, dy};
            unique_ptr<State> new_state = move_(move);
            if (new_state != nullptr) {
                result.emplace_back(move, std::move(new_state));
            }
        }
    }

    return result;
}


float State::h(){
    float cost_h = 0.0f;
    for (const auto& element : game->End_x) {
        const int block_idx = element.first;
        vector<int> x_end = element.second, y_end = game->End_y[block_idx];
        vector<int> xs = this->xs[block_idx], ys = this->ys[block_idx];

        if (xs.size() > 0){
            cost_h += abs(xs[0] - x_end[0]) + abs(ys[0] - y_end[0]);
        }
    }
    return cost_h;
}

bool State::operator==(const State& other) const {
    return this->hash_id == other.hash_id && this->pattern == other.pattern;
}

bool State::is_terminal() const {
    for (const auto& entry : this->game->End_x) {
        const int block_id = entry.first;
        const auto& x_coords = entry.second;
        const auto& y_coords = this->game->End_y.at(block_id);

        for (int i = 0; i < x_coords.size(); ++i) {
            int x = x_coords[i];
            int y = y_coords[i];

            // 检查当前状态的棋盘上这些位置是否都是对应的block_id
            if (this->board[x][y] != block_id) {
                return false; // 如果任一位置不匹配，说明还没有达到终止状态
            }
        }
    }
    return true; // 所有指定的位置都匹配对应的block_id，达到终止状态
}


template<typename T>
void State::hash_combine(size_t& seed, const T& val) const {
    std::hash<T> hasher;
    seed ^= hasher(val) + 0x9e3779b9 + (seed<<6) + (seed>>2);
}