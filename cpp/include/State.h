//
// Created by hammer on 24-4-7.
//

#ifndef STATE_H
#define STATE_H

#include <vector>
#include <unordered_map>
#include <memory>
#include "Move.h"

class Klotski; // 前向声明

class State {
public:
    Klotski* game;
    std::vector<std::vector<int>> board;
    std::vector<std::vector<int>> pattern;
    size_t hash_id;
    std::unordered_map<int, std::vector<int>> xs, ys;
    State* parent;
    Move from_move_;
    int depth;

    State(Klotski* game, const std::vector<std::vector<int>>& board,
          const std::unordered_map<int, std::vector<int>>& xs = {},
          const std::unordered_map<int, std::vector<int>>& ys = {},
          State* parent = nullptr, Move from_move = Move(), int depth = 0);

    bool operator==(const State& other) const;
    bool is_terminal() const;
    float h();
    std::vector<std::pair<Move, std::unique_ptr<State>>> next_states();
    std::unique_ptr<State> move_(Move& move);

    template<typename T>
    void hash_combine(size_t& seed, const T& val) const;
};

#endif // STATE_H
