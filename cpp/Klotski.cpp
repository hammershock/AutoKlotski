//
// Klotski.cpp
// Created by hammer on 24-4-7.
//

#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <memory>
#include <cmath>
#include <utility> // 对于std::pair
#include <queue>
#include <algorithm>

#include "include/Klotski.h"
#include "include/State.h"

using namespace std;

Klotski::Klotski(const vector<vector<int>>& board, const vector<vector<int>>& end_pattern, int empty = 0) : board(board), end_pattern(end_pattern), empty(empty), steps(0) {
    // 根据开始和结束图案初始化：
    // 1. blockidx2blocknum_：将每个block_id同他们的数量映射关系
    // 2. end_x, end_y在棋盘中有效的结束位置
    // vector<vector<int>> end_pattern = {{0, 0, 0, 0},
    //                                    {0, 0, 0, 0},
    //                                    {0, 0, 0, 0},
    //                                    {0, 1, 1, 0},
    //                                    {0, 1, 1, 0}};
    // 例如在上述图案中end_x = {3, 3, 4, 4}, end_y = {1, 2, 1, 2}
    // 3. End_x, End_y在结束状态中某个block_id对应的位置, 例如还是在上述图案中：End_x[1] = {3, 3, 4, 4}, End_y[1] = {1, 2, 1, 2}
    // 其中0代表empty，判断是否结束时不考虑0的位置是否匹配，只考虑当前状态在结束图案非0的位置是否匹配

    for (int i = 0; i < board.size(); ++i) {
        for (int j = 0; j < board[i].size(); ++j) {
            if (board[i][j] != empty) {
                this->blockidx2blocknum_[board[i][j]]++;  // 计数++
            }
            if (end_pattern[i][j] != empty){
                this->End_x[end_pattern[i][j]].push_back(i);
                this->End_y[end_pattern[i][j]].push_back(j);
                this->end_x.push_back(i);
                this->end_y.push_back(j);
            }
        }
    }
    this->blockidx2blocknum_[empty] = 0;
    this->state = std::make_unique<State>(this, board);
}


vector<Move> Klotski::a_star() {
    auto cmp = [](const tuple<float, unique_ptr<State>, vector<Move>>& a, const tuple<float, unique_ptr<State>, vector<Move>>& b) {
        return get<0>(a) > get<0>(b); // 比较f(n)值
    };
    priority_queue<tuple<float, unique_ptr<State>, vector<Move>>, vector<tuple<float, unique_ptr<State>, vector<Move>>>, decltype(cmp)> openSet(cmp);

    unordered_set<size_t> closedSet;

    auto initial_state = make_unique<State>(this, board, unordered_map<int, vector<int>>(), unordered_map<int, vector<int>>(), nullptr, Move(), 0);
    float initial_h = initial_state->h();
    openSet.push(make_tuple(initial_h, std::move(initial_state), vector<Move>()));

    while (!openSet.empty()) {
        const auto& current_tuple_ref = openSet.top();

        // 现在对unique_ptr进行移动操作，使用std::move确保调用的是移动构造函数
        unique_ptr<State> current_state = std::move(const_cast<unique_ptr<State>&>(std::get<1>(current_tuple_ref)));

        // 由于路径是一个vector，可以直接拷贝或移动
        vector<Move> path = std::get<2>(current_tuple_ref); // 这里可以直接复制，因为vector支持拷贝

        // 执行pop操作，移除队列顶部元素
        openSet.pop();
        if (current_state->is_terminal()) {
            this->steps = closedSet.size();
            return path;
        }

        size_t current_hash = current_state->hash_id;
        if (closedSet.find(current_hash) != closedSet.end()) {
            continue;   // 存在
        }
        closedSet.insert(current_hash);

        for (auto& [move, next_state] : current_state->next_states()) {
            if (closedSet.find(next_state->hash_id) == closedSet.end()) {
                float tentative_g = current_state->depth + 1;
                float h = next_state->h();
                float f = tentative_g + h;
                vector<Move> new_path = path;
                new_path.push_back(move);
                openSet.push(make_tuple(f, std::move(next_state), std::move(new_path)));
            }
        }
    }
    this->steps = closedSet.size();
    return {};
}
