#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // 为了自动转换 STL 容器
#include "include/Klotski.h"

namespace py = pybind11;

PYBIND11_MODULE(klotski_module, m) {
    py::class_<Move>(m, "Move")
        .def(py::init<int, int, int>())
        .def_readwrite("block_idx", &Move::block_idx)
        .def_readwrite("dx", &Move::dx)
        .def_readwrite("dy", &Move::dy);

    py::class_<Klotski>(m, "Klotski")
        .def(py::init<const std::vector<std::vector<int>>&, const std::vector<std::vector<int>>&, int>())
        .def("a_star", &Klotski::a_star)
        .def_readwrite("steps", &Klotski::steps);
}
