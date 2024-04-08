//
// Created by hammer on 24-4-7.
//

#ifndef MOVE_H
#define MOVE_H

struct Move {
    int block_idx = -1;
    int dx = 0;
    int dy = 0;
    Move() = default;
    Move(int b, int x, int y) : block_idx(b), dx(x), dy(y) {}
};

#endif // MOVE_H
