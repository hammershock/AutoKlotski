//
// Created by hammer on 24-4-7.
//

#ifndef KLOTSKI_H
#define KLOTSKI_H

#include <vector>
#include <unordered_map>
#include "State.h"

class Klotski {
public:
    std::vector<std::vector<int>> board;
    std::vector<std::vector<int>> end_pattern;
    int empty;
    int steps;

    std::unordered_map<int, int> blockidx2blocknum_;
    std::unique_ptr<State> state;
    std::vector<int> end_x;
    std::vector<int> end_y;
    std::unordered_map<int, std::vector<int>> End_x;
    std::unordered_map<int, std::vector<int>> End_y;

    Klotski(const std::vector<std::vector<int>>& board, const std::vector<std::vector<int>>& end_pattern, int empty);

    std::vector<Move> a_star();
};

#endif // KLOTSKI_H

